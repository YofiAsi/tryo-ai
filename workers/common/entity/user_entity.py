from datetime import datetime, timezone
import uuid

from beanie import Document, Update, Replace, before_event
from pydantic import EmailStr, Field
from app.consts import UserRole


class User(Document):
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    # OAuth2 fields
    google_id: str | None = None
    auth_provider: str = "email"  # "email" or "google"
    picture: str | None = None
    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login: datetime | None = None

    class Settings:
        name = "users"
        validate_on_save = True
        indexes = [
            "email",
            "google_id",
            "auth_provider"
        ]

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"User: {self.name}, {self.email}, {self.role.value}, {self.is_active}"
