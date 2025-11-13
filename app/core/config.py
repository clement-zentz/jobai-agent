# SPDX-License-Identifier: AGPL-3.0-or-later
# app/core/config.py
import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "")

    class Config:
        env_file = ".env"

settings = Settings()