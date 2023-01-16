from databases import Database
from sqlalchemy import create_engine
import motor.motor_asyncio

DATABASE_URL = "postgresql://user:password@host:port/database"

engine = create_engine(DATABASE_URL)

db = Database(DATABASE_URL)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://user:password@host:port/database")
mongo = client.get_default_database()
