from os import environ

from dotenv import load_dotenv

load_dotenv()

from databases import Database
from sqlalchemy import MetaData

database = Database(environ["DB_URI"])
metadata = MetaData()
