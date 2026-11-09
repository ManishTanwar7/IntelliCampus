"""
IntelliCampus: Authentication Controller
Handles user credentials, encrypted storage, and session lifecycle.
"""
from typing import Optional, Dict, Any
from models.student import Student
from models.session import UserSession, UserCredential
from services.security_service import SecurityService

class AuthController:
    _current_student: Optional[Student] = None

    @classmethod
    def get_current_student(cls) -> Optional[Student]:
        if cls._current_student is None:
            # Prefer 25BCS11666 if available, else first student in DB
            user_student = Student.get_by_id("25BCS11666")
            if user_student:
                cls._current_student = user_student
            else:
                cls._current_student = Student.get_first_or_default()
        return cls._current_student

    @classmethod
    def set_current_student(cls, student: Student):
        cls._current_student = student

    @classmethod
    def save_credentials(cls, student_id: str, uims_id: str, plain_password: str, remember: bool = True) -> bool:
        encrypted_pwd, salt = SecurityService.encrypt_password(plain_password)
        cred = UserCredential(
            credential_id=None,
            student_id=student_id,
            uims_user_id=uims_id,
            encrypted_password=encrypted_pwd,
            encryption_salt=salt,
            is_remembered=remember,
            sync_status="SAVED"
        )
        return cred.save()

    @classmethod
    def get_saved_credentials(cls, student_id: str) -> Optional[Dict[str, str]]:
        cred = UserCredential.get_by_student_id(student_id)
        if cred and cred.is_remembered:
            try:
                decrypted = SecurityService.decrypt_password(cred.encrypted_password, cred.encryption_salt)
                return {
                    "uims_user_id": cred.uims_user_id,
                    "password": decrypted,
                    "last_sync_at": cred.last_sync_at or "Never"
                }
            except Exception:
                return None
        return None

    @classmethod
    def create_session(cls, student_id: str) -> UserSession:
        return UserSession.create_new(student_id)
