from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ModelWatch AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "modelwatch"
    
    SECRET_KEY: str = "modelwatch-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Drift thresholds
    PSI_LOW: float = 0.1
    PSI_MEDIUM: float = 0.25
    JS_LOW: float = 0.1
    JS_MEDIUM: float = 0.2
    KS_ALPHA: float = 0.05
    
    # Quality thresholds
    NULL_RATE_WARN: float = 0.05
    NULL_RATE_CRIT: float = 0.15
    OUTLIER_RATE_WARN: float = 0.02
    
    # Health score
    HEALTH_WARN: float = 80.0
    HEALTH_CRIT: float = 60.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()