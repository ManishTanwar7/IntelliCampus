"""
Session and Credentials Model
"""
import uuid
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from services.database import DatabaseManager

@dataclass
class UserSession:
    session_id: str
    student_id: str
    token: Optional[str] = None
    cookies_json: Optional[str] = None
    is_active: bool = True
    last_activity: Optional[str] = None
    expires_at: Optional[str] = None

    @classmethod
    def create_new(cls, student_id: str, cookies: Optional[Dict[str, Any]] = None) -> 'UserSession':
        db = DatabaseManager()
        # Invalidate previous sessions
        db.execute_update("UPDATE sessions SET is_active = 0 WHERE student_id = %s;", (student_id,))
        
        session_id = str(uuid.uuid4())
        cookies_str = json.dumps(cookies) if cookies else "{}"
        query = """
            INSERT INTO sessions (session_id, student_id, cookies_json, is_active)
            VALUES (%s, %s, %s, 1);
        """
        db.execute_update(query, (session_id, student_id, cookies_str))
        return cls(session_id=session_id, student_id=student_id, cookies_json=cookies_str, is_active=True)

    @classmethod
    def get_active(cls, student_id: str) -> Optional['UserSession']:
        db = DatabaseManager()
        query = "SELECT * FROM sessions WHERE student_id = %s AND is_active = 1 ORDER BY created_at DESC LIMIT 1;"
        row = db.fetch_one(query, (student_id,))
        if row:
            return cls(
                session_id=row["session_id"],
                student_id=row["student_id"],
                token=row.get("token"),
                cookies_json=row.get("cookies_json"),
                is_active=bool(row.get("is_active", 1)),
                last_activity=str(row.get("last_activity")),
                expires_at=str(row.get("expires_at"))
            )
        return None


@dataclass
class UserCredential:
    credential_id: Optional[int]
    student_id: str
    uims_user_id: str
    encrypted_password: str
    encryption_salt: str
    is_remembered: bool = False
    last_sync_at: Optional[str] = None
    sync_status: str = "IDLE"

    @classmethod
    def get_by_student_id(cls, student_id: str) -> Optional['UserCredential']:
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM user_credentials WHERE student_id = %s;", (student_id,))
        if row:
            return cls(
                credential_id=row.get("credential_id"),
                student_id=row["student_id"],
                uims_user_id=row["uims_user_id"],
                encrypted_password=row["encrypted_password"],
                encryption_salt=row["encryption_salt"],
                is_remembered=bool(row.get("is_remembered", 0)),
                last_sync_at=str(row.get("last_sync_at")) if row.get("last_sync_at") else None,
                sync_status=row.get("sync_status", "IDLE")
            )
        return None

    def save(self) -> bool:
        db = DatabaseManager()
        existing = db.fetch_one("SELECT credential_id FROM user_credentials WHERE student_id = %s;", (self.student_id,))
        if existing:
            query = """
                UPDATE user_credentials SET
                    uims_user_id = %s, encrypted_password = %s,
                    encryption_salt = %s, is_remembered = %s,
                    last_sync_at = %s, sync_status = %s
                WHERE student_id = %s;
            """
            db.execute_update(query, (
                self.uims_user_id, self.encrypted_password,
                self.encryption_salt, 1 if self.is_remembered else 0,
                self.last_sync_at, self.sync_status, self.student_id
            ))
        else:
            query = """
                INSERT INTO user_credentials (student_id, uims_user_id, encrypted_password, encryption_salt, is_remembered, sync_status)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            self.credential_id = db.execute_update(query, (
                self.student_id, self.uims_user_id, self.encrypted_password,
                self.encryption_salt, 1 if self.is_remembered else 0, self.sync_status
            ))
        return True
