from pathlib import Path

from dotenv import dotenv_values


def get_app_env_values(env_path: str | Path) -> dict[str, str]:
    config = dotenv_values(str(env_path))
    return config
