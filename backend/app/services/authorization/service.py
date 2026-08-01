from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import timedelta
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT
from app.models.schemas import (
    AuthorizationGrant,
    AuthorizationTokenMetadata,
    AuthorizationTokenStatus,
    SemanticFrame,
    VehicleState,
    WorkflowEventType,
    make_id,
    utc_now,
)
from app.services.workflow.repository import WorkflowRepository


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def state_snapshot_digest(state: VehicleState) -> str:
    data = state.model_dump(mode="json", exclude={"updated_at"})
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuthorizationTokenError(ValueError):
    pass


class AuthorizationTokenService:
    def __init__(
        self,
        config: dict[str, Any],
        repository: WorkflowRepository,
        *,
        secret: bytes | None = None,
    ) -> None:
        self.config = config
        self.repository = repository
        self.ttl_seconds = int(config.get("token_ttl_seconds", 30))
        self.executable_actions = set(config.get("executable_actions", []))
        if secret is not None:
            self._secret = secret
            self.secret_source = "injected_test_secret"
        else:
            self._secret, self.secret_source = self._load_secret()

    def _load_secret(self) -> tuple[bytes, str]:
        env_name = str(
            self.config.get("secret_environment_variable", "YUZHENG_TOKEN_SECRET")
        )
        env_value = os.getenv(env_name)
        if env_value:
            return env_value.encode("utf-8"), "environment_variable"
        relative = Path(str(self.config.get("secret_file", "data/secrets/authorization.key")))
        path = relative if relative.is_absolute() else PROJECT_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path.read_bytes(), "local_file"
        value = secrets.token_bytes(32)
        path.write_bytes(value)
        return value, "local_file"

    def is_executable(self, frame: SemanticFrame) -> bool:
        return f"{frame.action}|{frame.target}" in self.executable_actions

    def issue(
        self,
        *,
        root_turn_id: str,
        turn_id: str,
        frame: SemanticFrame,
        state: VehicleState,
    ) -> AuthorizationGrant:
        active = self.repository.active_token_for_turn(turn_id)
        if active is not None and active.expires_at > utc_now():
            raise AuthorizationTokenError("当前轮次已有有效授权令牌")
        issued_at = utc_now()
        expires_at = issued_at + timedelta(seconds=self.ttl_seconds)
        token_id = make_id("TOK")
        nonce = secrets.token_urlsafe(24)
        snapshot_digest = state_snapshot_digest(state)
        payload = {
            "token_id": token_id,
            "root_turn_id": root_turn_id,
            "turn_id": turn_id,
            "action": frame.action,
            "target": frame.target,
            "area": frame.area,
            "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
            "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
            "nonce": nonce,
            "state_snapshot_digest": snapshot_digest,
        }
        payload_bytes = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        encoded_payload = _b64encode(payload_bytes)
        signature = hmac.new(
            self._secret, encoded_payload.encode("ascii"), hashlib.sha256
        ).digest()
        raw_token = f"{encoded_payload}.{_b64encode(signature)}"
        token_digest = signature.hex()
        metadata = AuthorizationTokenMetadata(
            token_id=token_id,
            root_turn_id=root_turn_id,
            turn_id=turn_id,
            action=frame.action,
            target=frame.target,
            area=frame.area,
            issued_at=issued_at,
            expires_at=expires_at,
            state_snapshot_digest=snapshot_digest,
            token_digest=token_digest,
            status=AuthorizationTokenStatus.ISSUED,
        )
        self.repository.insert_token(
            metadata, nonce_digest=hashlib.sha256(nonce.encode("utf-8")).hexdigest()
        )
        self.repository.append_event(
            root_turn_id=root_turn_id,
            related_turn_id=turn_id,
            event_type=WorkflowEventType.TOKEN_ISSUED,
            payload={
                "token_id": token_id,
                "token_digest": token_digest,
                "expires_at": metadata.expires_at.isoformat(),
                "state_snapshot_digest": snapshot_digest,
            },
        )
        return AuthorizationGrant(authorization_token=raw_token, metadata=metadata)

    def decode_and_validate(
        self,
        raw_token: str,
        *,
        expected_turn_id: str | None = None,
        expected_action: str | None = None,
        expected_target: str | None = None,
    ) -> tuple[dict[str, Any], AuthorizationTokenMetadata]:
        try:
            encoded_payload, encoded_signature = raw_token.split(".", 1)
            supplied_signature = _b64decode(encoded_signature)
            expected_signature = hmac.new(
                self._secret, encoded_payload.encode("ascii"), hashlib.sha256
            ).digest()
            if not hmac.compare_digest(supplied_signature, expected_signature):
                raise AuthorizationTokenError("授权令牌摘要不匹配")
            payload = json.loads(_b64decode(encoded_payload).decode("utf-8"))
        except AuthorizationTokenError:
            raise
        except Exception as exc:
            raise AuthorizationTokenError("授权令牌格式无效") from exc
        token_id = str(payload.get("token_id", ""))
        metadata = self.repository.get_token(token_id)
        if metadata is None:
            raise AuthorizationTokenError("授权令牌不存在")
        if not hmac.compare_digest(metadata.token_digest, expected_signature.hex()):
            raise AuthorizationTokenError("授权令牌与持久化摘要不一致")
        if metadata.status != AuthorizationTokenStatus.ISSUED:
            raise AuthorizationTokenError(f"授权令牌状态不可用: {metadata.status.value}")
        if metadata.expires_at <= utc_now():
            self.repository.transition_token(
                token_id,
                from_status=AuthorizationTokenStatus.ISSUED,
                to_status=AuthorizationTokenStatus.EXPIRED,
                reason="授权令牌已过期",
            )
            self.repository.append_event(
                root_turn_id=metadata.root_turn_id,
                related_turn_id=metadata.turn_id,
                event_type=WorkflowEventType.TOKEN_EXPIRED,
                payload={"token_id": token_id, "token_digest": metadata.token_digest},
            )
            raise AuthorizationTokenError("授权令牌已过期")
        bindings = {
            "turn_id": expected_turn_id,
            "action": expected_action,
            "target": expected_target,
        }
        for field, expected in bindings.items():
            if expected is not None and str(payload.get(field)) != expected:
                raise AuthorizationTokenError(f"授权令牌{field}绑定不匹配")
        return payload, metadata

    def metadata_from_untrusted_token(
        self, raw_token: str
    ) -> AuthorizationTokenMetadata | None:
        """Best-effort lookup used only to audit a rejected token attempt."""
        try:
            encoded_payload = raw_token.split(".", 1)[0]
            payload = json.loads(_b64decode(encoded_payload).decode("utf-8"))
            return self.repository.get_token(str(payload.get("token_id", "")))
        except Exception:
            return None

    def consume(self, metadata: AuthorizationTokenMetadata) -> bool:
        return self.repository.transition_token(
            metadata.token_id,
            from_status=AuthorizationTokenStatus.ISSUED,
            to_status=AuthorizationTokenStatus.CONSUMED,
            reason="执行前复查通过并原子消费",
        )

    def reject(self, metadata: AuthorizationTokenMetadata, reason: str) -> None:
        changed = self.repository.transition_token(
            metadata.token_id,
            from_status=AuthorizationTokenStatus.ISSUED,
            to_status=AuthorizationTokenStatus.REJECTED,
            reason=reason,
        )
        if changed:
            self.repository.append_event(
                root_turn_id=metadata.root_turn_id,
                related_turn_id=metadata.turn_id,
                event_type=WorkflowEventType.TOKEN_REJECTED,
                payload={
                    "token_id": metadata.token_id,
                    "token_digest": metadata.token_digest,
                    "reason": reason,
                },
            )
