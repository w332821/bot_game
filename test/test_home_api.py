from sqlalchemy import text
import pytest
from httpx import AsyncClient
from biz.application import app
from base.init_db import get_database_uri_from_config, get_mysql_sync_engine

def _insert_online_status():
    uri = get_database_uri_from_config()
    engine = get_mysql_sync_engine(uri)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM online_status"))
        conn.execute(text("INSERT INTO online_status(user_id, platform, last_seen, created_at, updated_at) VALUES('u1','web',NOW(),NOW(),NOW())"))
        conn.execute(text("INSERT INTO online_status(user_id, platform, last_seen, created_at, updated_at) VALUES('u2','app',NOW(),NOW(),NOW())"))

def _insert_online_metrics(metric_date: str):
    uri = get_database_uri_from_config()
    engine = get_mysql_sync_engine(uri)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM online_metrics WHERE metric_date = :d"), {"d": metric_date})
        conn.execute(text("INSERT INTO online_metrics(metric_date, time_slot, web_count, app_count, total_count, created_at) VALUES(:d,'00:00',5,3,8,NOW())"), {"d": metric_date})
        conn.execute(text("INSERT INTO online_metrics(metric_date, time_slot, web_count, app_count, total_count, created_at) VALUES(:d,'00:30',6,4,10,NOW())"), {"d": metric_date})

@pytest.mark.asyncio
async def test_home_online_count(auth_headers):
    _insert_online_status()
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/home/online-count", params={"windowMinutes": 5}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert data["total"] >= 2

@pytest.mark.asyncio
async def test_home_online_trend(auth_headers):
    metric_date = "2025-11-10"
    _insert_online_metrics(metric_date)
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/home/online-trend", params={"date": metric_date}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert len(data["dates"]) >= 2