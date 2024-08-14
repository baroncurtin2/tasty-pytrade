from pathlib import Path

from tastytrade.utils import get_app_env_values

APP_ENV_PATH = Path(__file__).parents[1] / "app.env"
APP_ENV_CONFIG = get_app_env_values(APP_ENV_PATH)
