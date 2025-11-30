# SPDX-License-Identifier: AGPL-3.0-or-later
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    raw_fixture_dir: str
    net_fixture_dir: str 

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

def get_settings() -> Settings:
    return Settings() # type: ignore[call-arg]

settings = get_settings()
