import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models.user import User

logger = logging.getLogger(__name__)


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    name: str,
    birth_date: str,
    birth_time: str | None,
    birth_place: str,
) -> User:
    user = User(
        telegram_id=telegram_id,
        name=name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
    )
    session.add(user)
    try:
        await session.flush()
        logger.info("Created user telegram_id=%s name=%r", telegram_id, name)
    except IntegrityError:
        await session.rollback()
        logger.warning("User telegram_id=%s already exists, fetching existing", telegram_id)
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one()
    return user


async def update_user(
    session: AsyncSession,
    telegram_id: int,
    **kwargs,
) -> User | None:
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is None:
        logger.warning("update_user: user telegram_id=%s not found", telegram_id)
        return None
    allowed_fields = {"name", "birth_date", "birth_time", "birth_place"}
    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(user, field, value)
        else:
            logger.warning("update_user: ignoring unknown field %r", field)
    await session.flush()
    logger.info("Updated user telegram_id=%s fields=%s", telegram_id, list(kwargs.keys()))
    return user


async def delete_user(session: AsyncSession, telegram_id: int) -> bool:
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is None:
        logger.warning("delete_user: user telegram_id=%s not found", telegram_id)
        return False
    await session.delete(user)
    await session.flush()
    logger.info("Deleted user telegram_id=%s", telegram_id)
    return True
