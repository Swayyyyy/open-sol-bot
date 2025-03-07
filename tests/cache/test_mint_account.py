import asyncio

import pytest
from solbot_cache.mint_account import MintAccountCache
from solbot_common.models import MintAccount
from solbot_db.session import init_db, start_session
from solders.pubkey import Pubkey
from sqlmodel import delete, select


@pytest.mark.asyncio
async def test_get_mint_account():
    init_db()
    mint = Pubkey.from_string("HiPZWtXxEvgzKnMBfHGvZqHfvgaJ1YHZVhwai1Wd8t4J")

    with start_session() as session:
        stmt = delete(MintAccount).where(MintAccount.mint == str(mint))  # type: ignore
        session.exec(statement=stmt)  # type: ignore
        session.commit()

    cache = MintAccountCache()
    mint_account = await cache.get_mint_account(mint)
    assert mint_account
    print(mint_account)
    # 等待写入数据库
    await asyncio.sleep(1)

    with start_session() as session:
        select_stmt = select(MintAccount).where(MintAccount.mint == mint)
        mint_account = session.exec(statement=select_stmt).one()
        assert mint_account
