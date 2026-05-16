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
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Settings:
        name = "users"
        validate_on_save = True
        indexes = [
            "email",
        ]

    @before_event(Update, Replace)
    def before_update(self):
        """Automatically update the updated_at field before saving"""
        self.updated_at = datetime.now(timezone.utc)

    def __str__(self):
        return f"User: {self.name}, {self.email}, {self.role.value}, {self.is_active}"
