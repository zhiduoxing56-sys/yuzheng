from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AuthorizationGrant,
    AuthorizationKeyMetadata,
    AuthorizationTokenMetadata,
    AuthorizationTokenStatus,
    SemanticFrame,
    SemanticIntent,
    RuntimeCapabilityStatus,
    SemanticControlMode,
    VehicleState,
    WorkflowEventType,
    make_id,
    utc_now,
)
from app.core.redaction import SensitiveDataRedactor
from app.services.workflow.repository import WorkflowRepository
from app.services.command_identity import (
    IDENTITY_FIELDS,
    CanonicalCommandIdentity,
    CanonicalCommandIdentityError,
)
from app.services.vehicle.capabilities import (
    CanonicalCapabilityError,
    CanonicalCapabilityRegistry,
    ResolvedCanonicalCapability,
)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    decoded = base64.urlsafe_b64decode(value + padding)
    if _b64encode(decoded) != value:
        raise ValueError("non-canonical base64url encoding")
    return decoded


def state_snapshot_digest(state: VehicleState) -> str:
    data = state.model_dump(
        mode="json",
        exclude={
            "updated_at",
            "state_epoch_id",
            "started_at",
            "reset_count",
            "last_reset_at",
            "reset_reason",
        },
    )
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuthorizationTokenError(ValueError):
    pass


class AuthorizationKeyError(RuntimeError):
    pass


class AuthorizationTokenService:
    def __init__(
        self,
        config: dict[str, Any],
        repository: WorkflowRepository,
        *,
        secret: bytes | None = None,
        capability_provider: Callable[[], RuntimeCapabilityStatus] | None = None,
        command_capability_registry: CanonicalCapabilityRegistry | None = None,
        vehicle_adapter_provider: Callable[[], str] | None = None,
    ) -> None:
        self.config = config
        self.repository = repository
        self.ttl_seconds = int(config.get("token_ttl_seconds", 30))
        if "executable_actions" in config:
            raise AuthorizationKeyError(
                "authorization.yaml 不得保留 legacy executable_actions"
            )
        self.revoked_tokens_on_startup = 0
        self._capability_provider = capability_provider
        self._command_capability_registry = command_capability_registry
        self._vehicle_adapter_provider = vehicle_adapter_provider
        self.repository.expire_due_issued_tokens()
        if secret is not None:
            self._secret = self._validate_secret(secret, "injected_test_secret")
            self.secret_source = "injected_test_secret"
            self.key_metadata = self._activate_key(self._secret, self.secret_source)
        else:
            self._secret, self.secret_source, self.key_metadata = self._load_secret()

    @staticmethod
    def _validate_secret(value: bytes, source: str) -> bytes:
        if source == "local_file" and len(value) != 32:
            raise AuthorizationKeyError("授权密钥文件格式无效：必须为32字节")
        if source != "local_file" and not 32 <= len(value) <= 4096:
            raise AuthorizationKeyError("授权密钥长度无效：必须至少32字节")
        return value

    @staticmethod
    def _fingerprint(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    def _revoke_issued(self, reason: str) -> int:
        revoked = self.repository.revoke_all_issued_tokens(
            SensitiveDataRedactor.redact_text(reason)
        )
        self.revoked_tokens_on_startup += len(revoked)
        return len(revoked)

    def _activate_key(self, value: bytes, source: str) -> AuthorizationKeyMetadata:
        fingerprint = self._fingerprint(value)
        previous = self.repository.key_metadata()
        changed = previous is not None and previous.fingerprint != fingerprint
        if changed:
            self._revoke_issued(
                f"授权密钥指纹发生变化，旧密钥 {previous.key_id} 已失效"
            )
        version = previous.key_version + 1 if changed else (previous.key_version if previous else 1)
        created_at = utc_now() if changed or previous is None else previous.created_at
        metadata = AuthorizationKeyMetadata(
            key_id=f"KEY_{fingerprint[:16]}",
            key_version=version,
            created_at=created_at,
            fingerprint=fingerprint,
            source=source,
            status="ACTIVE",
        )
        self.repository.store_key_metadata(metadata)
        return metadata

    def _invalidate_and_fail(self, message: str) -> None:
        safe_message = SensitiveDataRedactor.redact_text(message)
        self._revoke_issued(safe_message)
        previous = self.repository.key_metadata()
        if previous is not None:
            self.repository.store_key_metadata(previous.model_copy(update={"status": "INVALID"}))
        raise AuthorizationKeyError(safe_message)

    def _load_secret(self) -> tuple[bytes, str, AuthorizationKeyMetadata]:
        env_name = str(
            self.config.get("secret_environment_variable", "YUZHENG_TOKEN_SECRET")
        )
        if env_name in os.environ:
            env_value = os.environ.get(env_name, "").encode("utf-8")
            try:
                value = self._validate_secret(env_value, "environment_variable")
            except AuthorizationKeyError as exc:
                self._invalidate_and_fail(str(exc))
            metadata = self._activate_key(value, "environment_variable")
            return value, "environment_variable", metadata
        key_file_env = str(
            self.config.get("secret_file_environment_variable", "YUZHENG_TOKEN_KEY_FILE")
        )
        configured_path = os.getenv(
            key_file_env,
            str(self.config.get("secret_file", "data/secrets/authorization.key")),
        )
        relative = Path(configured_path)
        path = relative if relative.is_absolute() else PROJECT_ROOT / relative
        if path.exists():
            try:
                raw = path.read_bytes()
            except OSError as exc:
                self._invalidate_and_fail(
                    f"授权密钥文件不可读: {type(exc).__name__}"
                )
            try:
                value = self._validate_secret(raw, "local_file")
            except AuthorizationKeyError as exc:
                self._invalidate_and_fail(str(exc))
            metadata = self._activate_key(value, "local_file")
            return value, "local_file", metadata
        self._revoke_issued("授权密钥文件丢失，旧ISSUED令牌已撤销")
        path.parent.mkdir(parents=True, exist_ok=True)
        value = secrets.token_bytes(32)
        try:
            path.write_bytes(value)
        except OSError as exc:
            raise AuthorizationKeyError(
                f"无法创建授权密钥文件: {type(exc).__name__}"
            ) from None
        metadata = self._activate_key(value, "local_file")
        return value, "local_file", metadata

    def _command_capabilities(self) -> CanonicalCapabilityRegistry:
        if self._command_capability_registry is None:
            self._command_capability_registry = CanonicalCapabilityRegistry(
                load_yaml("vehicle_actions.yaml")
            )
        return self._command_capability_registry

    def _vehicle_adapter(self) -> str:
        if self._vehicle_adapter_provider is not None:
            return str(self._vehicle_adapter_provider())
        return str(load_yaml("vehicle_actions.yaml").get("adapter", "simulator"))

    def _resolve_command(self, intent: SemanticIntent) -> ResolvedCanonicalCapability:
        try:
            return self._command_capabilities().resolve(
                intent, adapter=self._vehicle_adapter()
            )
        except CanonicalCapabilityError as exc:
            raise AuthorizationTokenError(
                f"CANONICAL_CAPABILITY_UNSUPPORTED: {exc}"
            ) from exc

    def is_executable(self, frame: SemanticFrame) -> bool:
        if not frame.intents:
            return False
        for intent in frame.intents:
            try:
                self._resolve_command(intent)
            except AuthorizationTokenError:
                return False
        return True

    def issue(
        self,
        *,
        root_turn_id: str,
        turn_id: str,
        frame: SemanticFrame,
        state: VehicleState,
    ) -> AuthorizationGrant:
        if len(frame.intents) != 1:
            raise AuthorizationTokenError("车辆执行授权当前要求恰好一个正式子意图")
        return self._issue_for_intent(
            root_turn_id=root_turn_id,
            turn_id=turn_id,
            intent=frame.intents[0],
            state=state,
            check_active=True,
        )

    def issue_multi(
        self,
        *,
        root_turn_id: str,
        turn_id: str,
        frame: SemanticFrame,
        state: VehicleState,
    ) -> list[AuthorizationGrant]:
        """多意图放行：逐意图签发执行令牌，不可执行的意图跳过。

        返回能成功签发的令牌列表（每个绑定对应意图），供前端选择执行哪个。
        """
        grants: list[AuthorizationGrant] = []
        for intent in frame.intents:
            try:
                grants.append(
                    self._issue_for_intent(
                        root_turn_id=root_turn_id,
                        turn_id=turn_id,
                        intent=intent,
                        state=state,
                        check_active=False,
                    )
                )
            except AuthorizationTokenError:
                # 该意图不在可执行能力内（如天窗/空调）或 area 未明确，跳过签发
                continue
        return grants

    def _issue_for_intent(
        self,
        *,
        root_turn_id: str,
        turn_id: str,
        intent: SemanticIntent,
        state: VehicleState,
        check_active: bool,
    ) -> AuthorizationGrant:
        resolved = self._resolve_command(intent)
        if self._capability_provider is not None:
            capability = self._capability_provider()
            if (
                capability.semantic_control_mode != SemanticControlMode.FULL
                or not capability.real_model_inference
            ):
                raise AuthorizationTokenError(
                    "SEMANTIC_MODEL_DEGRADED_EXECUTION_DENIED: 真实语义模型降级，禁止签发车辆执行授权"
                )
        active = None
        if check_active:
            active = self.repository.active_token_for_turn(turn_id)
        if active is not None and active.expires_at > utc_now():
            raise AuthorizationTokenError("当前轮次已有有效授权令牌")
        issued_at = utc_now()
        expires_at = issued_at + timedelta(seconds=self.ttl_seconds)
        token_id = make_id("TOK")
        nonce = secrets.token_urlsafe(24)
        nonce_digest = hashlib.sha256(nonce.encode("utf-8")).hexdigest()
        snapshot_digest = state_snapshot_digest(state)
        payload = {
            "token_id": token_id,
            "root_turn_id": root_turn_id,
            "turn_id": turn_id,
            **resolved.identity.as_dict(),
            "capability_contract_id": resolved.contract_id,
            "capability_contract_version": resolved.contract_version,
            "capability_contract_digest": resolved.contract_digest,
            "capability_adapter": resolved.adapter,
            # Display-only compatibility metadata; never used as a security binding.
            "display_action": intent.action,
            "display_target": intent.target,
            "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
            "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
            "nonce": nonce,
            "key_id": self.key_metadata.key_id,
            "key_version": self.key_metadata.key_version,
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
            action=intent.action,
            target=intent.target,
            area=resolved.identity.area,
            intent_id=resolved.identity.intent_id,
            mode=resolved.identity.mode,
            value=resolved.identity.value,
            direction=resolved.identity.direction,
            control_attribute=resolved.identity.control_attribute,
            capability_contract_id=resolved.contract_id,
            capability_contract_version=resolved.contract_version,
            capability_contract_digest=resolved.contract_digest,
            capability_adapter=resolved.adapter,
            issued_at=issued_at,
            expires_at=expires_at,
            state_snapshot_digest=snapshot_digest,
            token_digest=token_digest,
            key_id=self.key_metadata.key_id,
            key_version=self.key_metadata.key_version,
            nonce_digest=nonce_digest,
            status=AuthorizationTokenStatus.ISSUED,
        )
        self.repository.insert_token(metadata, nonce_digest=nonce_digest)
        self.repository.append_event(
            root_turn_id=root_turn_id,
            related_turn_id=turn_id,
            event_type=WorkflowEventType.TOKEN_ISSUED,
            payload={
                "token_id": token_id,
                "token_digest": token_digest,
                "expires_at": metadata.expires_at.isoformat(),
                "state_snapshot_digest": snapshot_digest,
                "key_id": self.key_metadata.key_id,
                "canonical_identity": resolved.identity.as_dict(),
                "capability_contract_id": resolved.contract_id,
                "capability_contract_version": resolved.contract_version,
                "capability_contract_digest": resolved.contract_digest,
                "capability_adapter": resolved.adapter,
            },
        )
        return AuthorizationGrant(authorization_token=raw_token, metadata=metadata)

    def decode_and_validate(
        self,
        raw_token: str,
        *,
        expected_turn_id: str | None = None,
        expected_intent: SemanticIntent | None = None,
    ) -> tuple[dict[str, Any], AuthorizationTokenMetadata]:
        try:
            encoded_payload, encoded_signature = raw_token.split(".", 1)
            try:
                supplied_signature = _b64decode(encoded_signature)
            except Exception as exc:
                raise AuthorizationTokenError("授权令牌摘要不匹配") from exc
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
        persisted_bindings = {
            "token_id": metadata.token_id,
            "root_turn_id": metadata.root_turn_id,
            "turn_id": metadata.turn_id,
            "state_snapshot_digest": metadata.state_snapshot_digest,
            "key_id": metadata.key_id,
        }
        for field, persisted in persisted_bindings.items():
            if str(payload.get(field, "")) != str(persisted):
                raise AuthorizationTokenError(
                    f"授权令牌与持久化 {field} 绑定不一致"
                )
        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not nonce or metadata.nonce_digest is None:
            raise AuthorizationTokenError("授权令牌缺少 nonce 持久化绑定")
        if not hmac.compare_digest(
            hashlib.sha256(nonce.encode("utf-8")).hexdigest(), metadata.nonce_digest
        ):
            raise AuthorizationTokenError("授权令牌 nonce 与持久化摘要不一致")
        payload_key_id = str(payload.get("key_id", "legacy"))
        if metadata.key_id not in {"legacy", self.key_metadata.key_id}:
            raise AuthorizationTokenError("授权令牌密钥标识已失效")
        if metadata.key_id != "legacy" and payload_key_id != metadata.key_id:
            raise AuthorizationTokenError("授权令牌密钥标识不匹配")
        if (
            metadata.key_version is None
            or payload.get("key_version") != metadata.key_version
            or metadata.key_version != self.key_metadata.key_version
        ):
            raise AuthorizationTokenError("授权令牌密钥版本已失效或不匹配")
        try:
            payload_issued_at = datetime.fromisoformat(
                str(payload["issued_at"]).replace("Z", "+00:00")
            )
            payload_expires_at = datetime.fromisoformat(
                str(payload["expires_at"]).replace("Z", "+00:00")
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthorizationTokenError("授权令牌时间绑定无效") from exc
        if (
            payload_issued_at != metadata.issued_at
            or payload_expires_at != metadata.expires_at
        ):
            raise AuthorizationTokenError("授权令牌时间与持久化记录不一致")
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
        if expected_turn_id is not None and str(payload.get("turn_id")) != expected_turn_id:
            raise AuthorizationTokenError("授权令牌turn_id绑定不匹配")
        if any(field not in payload for field in IDENTITY_FIELDS):
            raise AuthorizationTokenError(
                "LEGACY_TOKEN_CANONICAL_IDENTITY_MISSING: 旧 action|target Token 永久禁止执行"
            )
        try:
            payload_identity = self._command_capabilities().identity_projector.from_mapping(
                payload, require_formal=True
            )
        except CanonicalCommandIdentityError as exc:
            raise AuthorizationTokenError(f"授权令牌 canonical identity 无效: {exc}") from exc
        if metadata.intent_id is None or metadata.control_attribute is None:
            raise AuthorizationTokenError(
                "LEGACY_TOKEN_CANONICAL_IDENTITY_MISSING: 持久化 Token 缺少 canonical identity"
            )
        metadata_mapping = {
            "intent_id": metadata.intent_id,
            "area": metadata.area,
            "mode": metadata.mode,
            "value": metadata.value,
            "direction": metadata.direction,
            "control_attribute": metadata.control_attribute,
        }
        try:
            metadata_identity = self._command_capabilities().identity_projector.from_mapping(
                metadata_mapping, require_formal=True
            )
        except CanonicalCommandIdentityError as exc:
            raise AuthorizationTokenError(
                f"持久化 Token canonical identity 无效: {exc}"
            ) from exc
        if payload_identity != metadata_identity:
            raise AuthorizationTokenError("授权令牌与持久化 canonical identity 不一致")
        if expected_intent is not None:
            try:
                expected_identity = self._command_capabilities().identity_projector.project(
                    expected_intent, require_formal=True
                )
            except CanonicalCommandIdentityError as exc:
                raise AuthorizationTokenError(
                    f"预期 canonical identity 无效: {exc}"
                ) from exc
            if payload_identity != expected_identity:
                raise AuthorizationTokenError("授权令牌 canonical command 绑定不匹配")
        contract_fields = (
            "capability_contract_id",
            "capability_contract_version",
            "capability_contract_digest",
            "capability_adapter",
        )
        if any(payload.get(field) in {None, ""} for field in contract_fields):
            raise AuthorizationTokenError("授权令牌缺少 capability contract 绑定")
        for field in contract_fields:
            if payload.get(field) != getattr(metadata, field):
                raise AuthorizationTokenError(
                    f"授权令牌与持久化 {field} 不一致"
                )
        try:
            current = self._command_capabilities().resolve_identity(
                payload_identity, adapter=self._vehicle_adapter()
            )
        except CanonicalCapabilityError as exc:
            raise AuthorizationTokenError(
                f"CANONICAL_CAPABILITY_CHANGED_OR_UNSUPPORTED: {exc}"
            ) from exc
        if (
            current.contract_id != payload["capability_contract_id"]
            or current.contract_version != payload["capability_contract_version"]
            or current.contract_digest != payload["capability_contract_digest"]
            or current.adapter != payload["capability_adapter"]
        ):
            raise AuthorizationTokenError(
                "CANONICAL_CAPABILITY_CONTRACT_CHANGED: 能力合同变化，旧 Token 永久失效"
            )
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
