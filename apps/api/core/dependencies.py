import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from dependencies.auth import get_current_user
from models.user import User


async def get_db(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    yield session


async def get_current_org_id(current_user: User = Depends(get_current_user)) -> uuid.UUID:
    return current_user.org_id
