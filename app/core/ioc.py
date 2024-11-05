from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from app.core.config import settings
from app.core.db import AsyncSessionFactory, DbConnection
from app.services import AuthService, EmailService, RedisService, SecurityService


class AdaptersProvider(Provider):
    scope = Scope.REQUEST

    security_service = provide(SecurityService)

    @provide(scope=Scope.REQUEST)
    async def connection(self) -> AsyncGenerator[DbConnection]:
        session = AsyncSessionFactory()
        uow = DbConnection(session=session)
        yield uow
        await uow.close()

    @provide(scope=Scope.REQUEST)
    async def redis(self) -> AsyncGenerator[Redis]:
        async with Redis.from_url(settings.REDIS_URL) as unit_redis:
            yield unit_redis


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    auth = provide(AuthService)
    email = provide(EmailService)
    redis_service = provide(RedisService)
