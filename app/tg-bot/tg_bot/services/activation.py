import random
import string
import time
from datetime import datetime
from typing import Optional

from sqlmodel import select

from common.models.tg_bot.activation_code import ActivationCode
from common.models.tg_bot.user_license import UserLicense
from db.session import NEW_ASYNC_SESSION, provide_session


class ActivationCodeService:
    @provide_session
    async def generate_code(self, seconds: int, *, session=NEW_ASYNC_SESSION) -> str:
        """
        生成新的激活码
        :param seconds: 激活码激活后的有效时长
        :return: 生成的激活码
        """
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # 检查code是否已存在
            result = await session.execute(
                select(ActivationCode).where(ActivationCode.code == code)
            )
            if result.first() is None:
                break

        activation_code = ActivationCode(code=code, valid_seconds=seconds)
        session.add(activation_code)
        return code

    # @provide_session
    # async def is_code_valid(
    #     self, code: str, *, session=NEW_ASYNC_SESSION
    # ) -> bool:
    #     """
    #     检查激活码是否有效
    #     :param activation_code: 激活码
    #     :return: 是否有效
    #     """
    #     result = await session.execute(
    #         select(ActivationCode).where(ActivationCode.code == code)
    #     )
    #     activation_code = result.scalar_one_or_none()
    #     if activation_code is None:
    #         return False

    @provide_session
    async def activate_user(
        self, chat_id: int, code: str, *, session=NEW_ASYNC_SESSION
    ) -> bool:
        """
        激活用户
        :param chat_id: 用户的chat_id
        :param code: 激活码
        :return: (是否激活成功, 消息)
        """
        # 查询激活码
        result = await session.execute(
            select(ActivationCode).where(
                ActivationCode.code == code, ActivationCode.used == False
            )
        )
        activation_code = result.scalar_one_or_none()
        if not activation_code:
            return False

        # 更新激活码状态
        activation_code.used = True
        activation_code.used_by = chat_id
        activation_code.used_at = datetime.now()

        # 更新或创建用户授权
        result = await session.execute(
            select(UserLicense).where(UserLicense.chat_id == chat_id)
        )
        user_license = result.scalar_one_or_none()

        if user_license:
            user_license.expired_timestamp += activation_code.valid_seconds
        else:
            user_license = UserLicense(
                chat_id=chat_id,
                expired_timestamp=activation_code.valid_seconds + int(time.time()),
            )
            session.add(user_license)

        return True

    @provide_session
    async def get_user_license(
        self, chat_id: int, *, session=NEW_ASYNC_SESSION
    ) -> Optional[UserLicense]:
        """
        获取用户授权信息
        :param chat_id: 用户的chat_id
        :return: 用户授权信息
        """
        result = await session.execute(
            select(UserLicense).where(UserLicense.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    @provide_session
    async def is_user_authorized(
        self, chat_id: int, *, session=NEW_ASYNC_SESSION
    ) -> bool:
        """
        检查用户是否有可用时长
        :param chat_id: 用户的chat_id
        :return: 是否有可用时长
        """
        user_license = await self.get_user_license(chat_id, session=session)
        return user_license is not None and user_license.expired_timestamp > int(
            time.time()
        )

    @provide_session
    async def deduct_user_time(
        self, chat_id: int, seconds: int = 1, *, session=NEW_ASYNC_SESSION
    ) -> bool:
        """
        扣除用户使用时长
        :param chat_id: 用户的chat_id
        :param minutes: 要扣除的分钟数
        :return: 是否扣除成功
        """
        result = await session.execute(
            select(UserLicense).where(UserLicense.chat_id == chat_id)
        )
        user_license = result.scalar_one_or_none()

        if not user_license or user_license.expired_timestamp < seconds:
            return False

        user_license.expired_timestamp -= seconds
        return True

    @provide_session
    async def get_user_expired_timestamp(
        self, chat_id: int, *, session=NEW_ASYNC_SESSION
    ) -> int:
        """获取到期时间（秒）
        :param chat_id: 用户的chat_id
        :return: 用户到期时间（秒）
        """
        result = await session.execute(
            select(UserLicense.expired_timestamp).where(UserLicense.chat_id == chat_id)
        )
        return result.scalar_one_or_none() or 0
