import os


class Settings:
    """Runtime configuration loaded from environment variables."""

    def __init__(self) -> None:
        self.ENV = os.environ.get("ENV", "development")
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
        self.DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./meal_planner.db")
        self.REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

        # Auth
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # Caching
        self.CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "300"))


settings = Settings()

