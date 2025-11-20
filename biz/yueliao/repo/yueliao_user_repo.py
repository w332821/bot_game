from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
import os
import bcrypt
import random
from datetime import datetime


class YueliaoUserRepo:
    def __init__(self):
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/yueliao")
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client.yueliao
        self.users_collection = self.db.users

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Dict]:
        query = {}

        if search:
            query = {
                "$or": [
                    {"nickname": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"yueliaoId": {"$regex": search, "$options": "i"}}
                ]
            }

        cursor = self.users_collection.find(
            query,
            {"password": 0, "settings": 0, "friendRequests": 0}
        ).skip(skip).limit(limit).sort("createdAt", -1)

        users = await cursor.to_list(length=limit)

        for user in users:
            user["id"] = str(user.pop("_id"))
            if "friends" in user:
                user["friends"] = [str(f) for f in user["friends"]]

        return users

    async def get_user_count(self, search: Optional[str] = None) -> int:
        query = {}

        if search:
            query = {
                "$or": [
                    {"nickname": {"$regex": search, "$options": "i"}},
                    {"phone": {"$regex": search, "$options": "i"}},
                    {"yueliaoId": {"$regex": search, "$options": "i"}}
                ]
            }

        return await self.users_collection.count_documents(query)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        from bson import ObjectId

        try:
            user = await self.users_collection.find_one(
                {"_id": ObjectId(user_id)},
                {"password": 0}
            )

            if user:
                user["id"] = str(user.pop("_id"))
                if "friends" in user:
                    user["friends"] = [str(f) for f in user["friends"]]
                if "friendRequests" in user:
                    for req in user["friendRequests"]:
                        req["id"] = str(req.pop("_id"))
                        req["from"] = str(req["from"])

            return user
        except Exception:
            return None

    async def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        user = await self.users_collection.find_one(
            {"phone": phone},
            {"password": 0}
        )

        if user:
            user["id"] = str(user.pop("_id"))
            if "friends" in user:
                user["friends"] = [str(f) for f in user["friends"]]

        return user

    async def get_user_by_yueliao_id(self, yueliao_id: str) -> Optional[Dict]:
        user = await self.users_collection.find_one(
            {"yueliaoId": yueliao_id},
            {"password": 0}
        )

        if user:
            user["id"] = str(user.pop("_id"))
            if "friends" in user:
                user["friends"] = [str(f) for f in user["friends"]]

        return user

    async def create_yueliao_user(
        self,
        phone: str,
        password: str,
        nickname: Optional[str] = None
    ) -> str:
        existing_user = await self.users_collection.find_one({"phone": phone})
        if existing_user:
            raise ValueError(f"手机号 {phone} 已存在")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        yueliao_id = await self._generate_unique_yueliao_id()

        if nickname is None or nickname.strip() == "":
            nickname = f"用户{phone[-4:]}"

        avatar_num = random.randint(1, 100)
        avatar = f"/static/avatars/avatar-{avatar_num:03d}.png"

        now = datetime.utcnow()
        user_doc = {
            "phone": phone,
            "password": hashed_password,
            "nickname": nickname,
            "yueliaoId": yueliao_id,
            "avatar": avatar,
            "status": "offline",
            "lastSeen": now,
            "friends": [],
            "friendRequests": [],
            "qrCode": "",
            "settings": {
                "language": "zh-cn",
                "theme": "auto",
                "notifications": {
                    "messageSound": True,
                    "vibrate": True,
                    "showPreview": True
                }
            },
            "createdAt": now,
            "updatedAt": now
        }

        try:
            result = await self.users_collection.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            raise RuntimeError(f"创建悦聊用户失败: {str(e)}")

    async def _generate_unique_yueliao_id(self, max_retries: int = 10) -> str:
        for _ in range(max_retries):
            yueliao_id = ''.join([str(random.randint(0, 9)) for _ in range(8)])

            existing = await self.users_collection.find_one({"yueliaoId": yueliao_id})
            if not existing:
                return yueliao_id

        raise RuntimeError("无法生成唯一的悦聊ID，请重试")
