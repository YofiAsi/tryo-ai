import logging
from app.consts import UserRole
from app.entity import User

log = logging.getLogger(__name__)

async def init_user(email: str, name: str, role: UserRole):
    res = await User.find_one(User.email == email)
    if res:
        log.info("User already exists")
        return
    from datetime import datetime, timezone
    user_create = User(
        name=name,
        email=email,
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await User.create(user_create)
    log.info(f"User {email} created")

async def init_default_users():
    log.info("Initializing default user")
    users = []
    for user in users:
        await init_user(user["email"], user["name"], user["role"])
    log.info("Default users initialized")

async def init_migration():
    log.info("Initializing migration")
    await init_default_users()
    log.info("Migration initialized")
