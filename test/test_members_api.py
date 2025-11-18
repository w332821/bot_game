import pytest
from httpx import AsyncClient
from sqlalchemy import text
from biz.application import app
from base.init_db import get_database_uri_from_config, get_mysql_sync_engine

def _seed_members():
    uri = get_database_uri_from_config()
    engine = get_mysql_sync_engine(uri)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM login_logs"))
        conn.execute(text("DELETE FROM member_profiles"))
        conn.execute(text("DELETE FROM users"))
        conn.execute(text("INSERT INTO users(id, chat_id, username, balance, join_date, created_at, updated_at) VALUES('u100','c1','a2356a',0,CURDATE(),NOW(),NOW())"))
        conn.execute(text("INSERT INTO users(id, chat_id, username, balance, join_date, created_at, updated_at) VALUES('u101','c1','member001',1000,CURDATE(),NOW(),NOW())"))
        conn.execute(text("INSERT INTO member_profiles(user_id, account, plate, superior_account, open_time, company_remarks, created_at) VALUES('u100','a2356a','B','Dd12580',NOW(),'备注',NOW())"))
        conn.execute(text("INSERT INTO member_profiles(user_id, account, plate, superior_account, open_time, company_remarks, created_at) VALUES('u101','member001','B','agent001',NOW(),'备注',NOW())"))
        conn.execute(text("INSERT INTO login_logs(account, login_time, ip_address, ip_location, operator, created_at) VALUES('a2356a',NOW(),'223.104.76.98','中国-广州-广东','移动',NOW())"))

@pytest.mark.asyncio
async def test_members_list(auth_headers):
    _seed_members()
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/users/members", params={"page": 1, "pageSize": 10}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert isinstance(data["list"], list)
    assert data["total"] >= 2

@pytest.mark.asyncio
async def test_member_detail_and_login_log(auth_headers):
    _seed_members()
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/users/members/a2356a", headers=auth_headers)
        assert r.status_code == 200
        b = r.json()
        assert b["code"] == 200
        d = b["data"]
        assert d["account"] == "a2356a"
        r2 = await client.get("/api/users/members/a2356a/login-log", params={"page": 1, "pageSize": 10}, headers=auth_headers)
        assert r2.status_code == 200
        b2 = r2.json()
        assert b2["code"] == 200
        assert isinstance(b2["data"]["list"], list)