from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

class FBAccount(BaseModel):
    id: int
    user_id: int
    access_token: str

    def insert_one(self):
        db["fb_accounts"].insert_one(self.__dict__)

    def resolve_all_fb_accounts(self, info):
        return db["fb_accounts"].find({"is_active": True})

    def resolve_fb_account(self, info, user_id):
        return db["fb_accounts"].find_one({"user_id": user_id, "is_active": True})

    def resolve_fb_engagements(self, info, user_id):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        return db["fb_engagements"].find({"user_id": user_id, "date": {"$gte": start_date, "$lt": end_date}}).sort("date", -1)

    def resolve_summary(self, info, user_id):
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        result = db["fb_engagements"].find({"user_id": user_id, "date": {"$gte": start_date, "$lt": end_date}})
        total_likes = 0
        total_shares = 0
        total_comments = 0
        for engagement in result:
            total_likes += engagement["likes"]
            total_shares += engagement["shares"]
            total_comments += engagement["comments"]
        return Summary(total_likes=total_likes, total_shares=total_shares, total_comments=total_comments)
