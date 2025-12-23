# backend/db/base.py

from sqlalchemy.orm import DeclarativeBase


# Base for all SQLAlchemy models
class Base(DeclarativeBase):
    pass
