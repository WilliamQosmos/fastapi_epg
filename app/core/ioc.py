from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide

from app.core.db import AsyncSessionFactory, DbConnection


class AdaptersProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.REQUEST)
    async def connection(self) -> AsyncGenerator[DbConnection]:
        session = AsyncSessionFactory()
        uow = DbConnection(session=session)
        yield uow
        await uow.close()
