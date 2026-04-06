from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "RetinalAI"
    environment: str = "development"
    database_url: str = "sqlite:///./retinalai.db"
    reports_dir: str = "reports/generated"
    model_dir: str = "ml/models/weights"


settings = Settings()
