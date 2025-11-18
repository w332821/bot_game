import pytest
from httpx import AsyncClient
from biz.application import app

async def _create_draw(issue: str, game_type: str):
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.post("/api/add", json={
            "drawNumber": 1,
            "issue": issue,
            "drawCode": "1,2,3,4,5,6,7,8,9,10",
            "gameType": game_type,
            "isRandom": False,
            "chatId": "system",
            "betCount": 0
        })
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_lottery_results_list():
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    issue = f"{today}-001"
    await _create_draw(issue, "lucky8")
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/lottery/results", params={"page": 1, "pageSize": 10, "lotteryType": "168澳洲幸运8", "lotteryDate": datetime.now().strftime("%Y-%m-%d")})
    assert r.status_code == 200
    body = r.json()
    assert body["code"] == 200
    data = body["data"]
    assert isinstance(data["list"], list)
    assert data["page"] == 1
    assert data["pageSize"] == 10
    assert data["total"] >= 1

@pytest.mark.asyncio
async def test_lottery_result_detail():
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    issue = f"{today}-002"
    await _create_draw(issue, "lucky8")
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/lottery/results", params={"page": 1, "pageSize": 1, "lotteryType": "168澳洲幸运8", "lotteryDate": datetime.now().strftime("%Y-%m-%d")})
        body = r.json()["data"]
        assert len(body["list"]) >= 1
        first_id = body["list"][0]["id"]
        r2 = await client.get(f"/api/lottery/results/{first_id}")
        assert r2.status_code == 200
        b2 = r2.json()
        assert b2["code"] == 200
        d = b2["data"]
        assert d["id"] == first_id
        assert isinstance(d["numbers"], list)