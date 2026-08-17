from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class AuditSigningError(RuntimeError):
    """The signing boundary or signing material is unavailable or inconsistent."""


@dataclass(frozen=True)
class AuditSigningState:
    version: int
    algorithm: str
    start_rowid: int
    key_id: str
    public_key: str


class AuditSigner:
    """Database-external Ed25519 material for the existing audit hash chain."""

    _ALGORITHM = "Ed25519"

    def __init__(self, database_path: Path) -> None:
        keys_root = (
            database_path.parent.parent
            if database_path.parent.name == "database"
            else database_path.parent
        )
        keys_dir = keys_root / "keys"
        self.private_key_path = keys_dir / "audit_ed25519_private.pem"
        self.state_path = keys_dir / "audit_signing_state.json"

    @staticmethod
    def _key_id(public_key_raw: bytes) -> str:
        return hashlib.sha256(public_key_raw).hexdigest()

    def _load_private_key(self) -> Ed25519PrivateKey:
        if not self.private_key_path.exists():
            if self.state_path.exists():
                raise AuditSigningError("审计签名状态存在，但私钥文件缺失")
            self.private_key_path.parent.mkdir(parents=True, exist_ok=True)
            key = Ed25519PrivateKey.generate()
            self.private_key_path.write_bytes(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
            return key
        try:
            key = serialization.load_pem_private_key(
                self.private_key_path.read_bytes(), password=None
            )
        except Exception as exc:
            raise AuditSigningError(f"审计私钥不可读取: {type(exc).__name__}") from exc
        if not isinstance(key, Ed25519PrivateKey):
            raise AuditSigningError("审计私钥不是 Ed25519 私钥")
        return key

    @staticmethod
    def _public_raw(private_key: Ed25519PrivateKey) -> bytes:
        return private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    def _read_state(self) -> AuditSigningState | None:
        if not self.state_path.exists():
            return None
        try:
            data: dict[str, Any] = json.loads(self.state_path.read_text(encoding="utf-8"))
            state = AuditSigningState(
                version=int(data["version"]),
                algorithm=str(data["algorithm"]),
                start_rowid=int(data["start_rowid"]),
                key_id=str(data["key_id"]),
                public_key=str(data["public_key"]),
            )
        except Exception as exc:
            raise AuditSigningError(f"审计签名状态文件损坏: {type(exc).__name__}") from exc
        if state.version != 1 or state.algorithm != self._ALGORITHM or state.start_rowid < 1:
            raise AuditSigningError("审计签名状态文件内容无效")
        return state

    def read_state(self) -> AuditSigningState | None:
        """Read the fixed signing boundary without creating keys or state."""

        return self._read_state()

    def ensure_state(self, maximum_rowid: int) -> AuditSigningState:
        private_key = self._load_private_key()
        public_raw = self._public_raw(private_key)
        expected_key_id = self._key_id(public_raw)
        expected_public = base64.b64encode(public_raw).decode("ascii")
        state = self._read_state()
        if state is not None:
            if state.key_id != expected_key_id or state.public_key != expected_public:
                raise AuditSigningError("审计签名状态与当前私钥不匹配")
            return state
        state = AuditSigningState(
            version=1,
            algorithm=self._ALGORITHM,
            start_rowid=maximum_rowid + 1,
            key_id=expected_key_id,
            public_key=expected_public,
        )
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state.__dict__, ensure_ascii=False, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        return state

    def sign_current_hash(self, current_hash: str, *, maximum_rowid: int) -> tuple[str, AuditSigningState]:
        state = self.ensure_state(maximum_rowid)
        try:
            digest = bytes.fromhex(current_hash)
        except ValueError as exc:
            raise AuditSigningError("current_hash 不是十六进制 SHA-256 摘要") from exc
        signature = self._load_private_key().sign(digest)
        return base64.b64encode(signature).decode("ascii"), state

    @classmethod
    def verify(
        cls,
        current_hash: str,
        signature: str | None,
        signature_algorithm: str | None,
        signature_key_id: str | None,
        state: AuditSigningState,
    ) -> str | None:
        if not signature:
            return "SIGNATURE_MISSING"
        if signature_algorithm != cls._ALGORITHM or signature_key_id != state.key_id:
            return "SIGNATURE_METADATA_MISMATCH"
        try:
            public_key = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(state.public_key, validate=True)
            )
            public_key.verify(base64.b64decode(signature, validate=True), bytes.fromhex(current_hash))
        except Exception:
            return "SIGNATURE_INVALID"
        return None
