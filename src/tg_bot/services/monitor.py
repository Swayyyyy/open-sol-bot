from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from common.cp.monitor_events import MonitorEventProducer
from common.models.tg_bot.monitor import Monitor as MonitorModel
from db.redis import RedisClient
from db.session import NEW_ASYNC_SESSION, provide_session
from tg_bot.models.monitor import Monitor


def from_db_model(obj: MonitorModel) -> Monitor:
    monitor = Monitor(
        pk=obj.id,
        chat_id=obj.chat_id,
        target_wallet=obj.target_wallet,
        wallet_alias=obj.wallet_alias,
        active=obj.active,
    )

    return monitor


class MonitorService:
    def __init__(self) -> None:
        redis = RedisClient.get_instance()
        self.producer = MonitorEventProducer(redis)

    @provide_session
    async def get_by_chat_id(
        self, chat_id: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> Monitor | None:
        stmt = select(MonitorModel).where(MonitorModel.chat_id == chat_id)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return from_db_model(obj)

    @provide_session
    async def add(
        self, monitor: Monitor, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        """Add a new monitor to the database"""
        if monitor.target_wallet is None:
            raise ValueError("target_wallet is required")

        try:
            # 第一步：创建数据库记录
            db_monitor = MonitorModel(
                chat_id=monitor.chat_id,
                target_wallet=monitor.target_wallet,
                wallet_alias=monitor.wallet_alias,
                active=monitor.active,
            )
            session.add(db_monitor)
            await session.flush()  # 获取自动生成的 ID

            # 第二步：发送事件
            try:
                assert db_monitor.id, "ID should not be None"
                await self.producer.resume_monitor(
                    db_monitor.id,  # 使用数据库生成的 ID
                    db_monitor.target_wallet,
                    db_monitor.chat_id,
                )
            except Exception as e:
                await session.rollback()  # 如果发送事件失败，回滚数据库操作
                raise ValueError(f"Failed to send monitor event: {e}")

            # 所有操作都成功，提交事务
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to create monitor: {e}")

    @provide_session
    async def addall(
        self, monitors: List[Monitor], *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        """Add a new monitor to the database"""
        try:
            # 第一步：创建数据库记录
            db_monitors = [MonitorModel(
                chat_id=monitor.chat_id,
                target_wallet=monitor.target_wallet,
                wallet_alias=monitor.wallet_alias,
                active=monitor.active,
            ) for monitor in monitors]
            session.add_all(db_monitors)
            await session.flush()  # 获取自动生成的 ID

            # 第二步：发送事件
            try:
                assert db_monitors[1].id, "ID should not be None"
                await self.producer.resume_many_monitor(
                    db_monitors[1].id,  # 使用数据库生成的 ID
                    ','.join([db_monitor.target_wallet for db_monitor in db_monitors]),
                    db_monitors[1].chat_id,
                )
            except Exception as e:
                await session.rollback()  # 如果发送事件失败，回滚数据库操作
                raise ValueError(f"Failed to send monitor event: {e}")

            # 所有操作都成功，提交事务
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to create monitor: {e}")

    @provide_session
    async def update(
        self, monitor: Monitor, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        """Update an existing monitor in the database"""
        if monitor.target_wallet is None:
            raise ValueError("target_wallet is required")

        obj = select(MonitorModel).where(MonitorModel.id == monitor.pk).limit(1)
        obj = (await session.execute(obj)).scalar_one_or_none()
        if obj is None:
            raise ValueError(f"Copytrade with pk {monitor.pk} not found")
        obj.target_wallet = monitor.target_wallet
        obj.wallet_alias = monitor.wallet_alias
        old_active = obj.active
        obj.active = monitor.active
        session.add(obj)
        try:
            assert obj.id, "ID should not be None"
            if old_active is False and obj.active is True:
                await self.producer.resume_monitor(
                    obj.id,
                    obj.target_wallet,
                    obj.chat_id,
                )
            elif old_active is True and obj.active is False:
                await self.producer.pause_monitor(
                    obj.id,
                    obj.target_wallet,
                    obj.chat_id,
                )
        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to update monitor: {e}")
        await session.commit()

    @provide_session
    async def delete(
        self, monitor: Monitor, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        """Delete a monitor from the database"""
        if monitor.pk is None:
            raise ValueError("pk is required")

        stmt = select(MonitorModel).where(MonitorModel.id == monitor.pk)
        obj = (await session.execute(stmt)).scalar_one_or_none()
        if obj is None:
            return
        await session.delete(obj)
        try:
            assert obj.id, "ID should not be None"
            await self.producer.pause_monitor(
                obj.id,
                obj.target_wallet,
                obj.chat_id,
            )
        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to delete monitor: {e}")
        await session.commit()

    @provide_session
    async def list(self, *, session: AsyncSession = NEW_ASYNC_SESSION) -> list[Monitor]:
        """Get all monitors from the database"""
        stmt = select(MonitorModel)
        result = await session.execute(stmt)
        return [
            Monitor(
                pk=row.id,
                chat_id=row.chat_id,
                target_wallet=row.target_wallet,
                wallet_alias=row.wallet_alias,
                active=row.active,
            )
            for row in result.scalars()
        ]

    @provide_session
    async def get_by_id(
        self, pk: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> Monitor:
        """Get a monitor by pk from the database"""
        stmt = select(MonitorModel).where(MonitorModel.id == pk).limit(1)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise ValueError(f"Monitor with pk {pk} not found")

        return from_db_model(obj)

    @provide_session
    async def list_by_owner(
        self, chat_id: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> List[Monitor]:
        stmt = select(MonitorModel).where(MonitorModel.chat_id == chat_id)

        results = await session.execute(stmt)
        return [
            Monitor(
                pk=row.id,
                chat_id=chat_id,
                target_wallet=row.target_wallet,
                wallet_alias=row.wallet_alias,
                active=row.active,
            )
            for row in results.scalars()
        ]

    @provide_session
    async def get_chat_ids_by_target_wallet(
        self, target_wallet: str, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> List[int]:
        stmt = select(MonitorModel).where(MonitorModel.target_wallet == target_wallet)
        results = await session.execute(stmt)
        return [row.chat_id for row in results.scalars()]

    @provide_session
    async def get_active_by_target_wallet(
        self, target_wallet: str, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> List[Monitor]:
        stmt = select(MonitorModel).where(
            MonitorModel.target_wallet == target_wallet, MonitorModel.active == True
        )
        results = await session.execute(stmt)
        return [from_db_model(obj) for obj in results.scalars()]

    @provide_session
    async def inactive_all(
        self, chat_id: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        _handled = []
        stmt = select(MonitorModel).where(MonitorModel.chat_id == chat_id)
        results = await session.execute(stmt)
        for obj in results.scalars():
            obj.active = False
            session.add(obj)
            try:
                assert obj.id, "ID should not be None"
                data = {
                    "monitor_id": obj.id,
                    "target_wallet": obj.target_wallet,
                    "owner_id": obj.chat_id,
                }
                await self.producer.pause_monitor(**data)
                _handled.append(data)
            except Exception as e:
                await session.rollback()
                for data in _handled:
                    await self.producer.resume_monitor(**data)
                raise ValueError(f"Failed to update monitor: {e}")
        await session.commit()

    @provide_session
    async def active_all(
        self, chat_id: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        _handled = []
        stmt = select(MonitorModel).where(MonitorModel.chat_id == chat_id)
        results = await session.execute(stmt)
        for obj in results.scalars():
            obj.active = True
            session.add(obj)
            try:
                assert obj.id, "ID should not be None"
                data = {
                    "monitor_id": obj.id,
                    "target_wallet": obj.target_wallet,
                    "owner_id": obj.chat_id,
                }
                await self.producer.resume_monitor(**data)
                _handled.append(data)
            except Exception as e:
                await session.rollback()
                for data in _handled:
                    await self.producer.resume_monitor(**data)
                raise ValueError(f"Failed to update monitor: {e}")
        await session.commit()

    @provide_session
    async def active(
        self, chat_id: int, pk: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        stmt = select(MonitorModel).where(
            MonitorModel.id == pk, MonitorModel.chat_id == chat_id
        )
        results = await session.execute(stmt)
        obj = results.scalar_one_or_none()
        if obj is None:
            raise ValueError(f"Monitor with pk {pk} not found")
        obj.active = True
        session.add(obj)
        try:
            assert obj.id, "ID should not be None"
            await self.producer.resume_monitor(
                obj.id,
                obj.target_wallet,
                obj.chat_id,
            )
        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to update monitor: {e}")
        await session.commit()

    @provide_session
    async def inactive(
        self, chat_id: int, pk: int, *, session: AsyncSession = NEW_ASYNC_SESSION
    ) -> None:
        stmt = select(MonitorModel).where(
            MonitorModel.id == pk, MonitorModel.chat_id == chat_id
        )
        results = await session.execute(stmt)
        obj = results.scalar_one_or_none()
        if obj is None:
            raise ValueError(f"Monitor with pk {pk} not found")
        obj.active = False
        session.add(obj)
        try:
            assert obj.id, "ID should not be None"
            await self.producer.pause_monitor(
                obj.id,
                obj.target_wallet,
                obj.chat_id,
            )
        except Exception as e:
            await session.rollback()
            raise ValueError(f"Failed to update monitor: {e}")
        await session.commit()
