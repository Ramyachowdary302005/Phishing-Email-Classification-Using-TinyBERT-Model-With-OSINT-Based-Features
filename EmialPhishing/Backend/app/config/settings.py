from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "Phishing Detection API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Model Configuration
    model_name: str = "huawei-noah/TinyBERT_General_4L_312D"
    max_token_length: int = 512
    model_cache_dir: str = "./models"
    
    # Dataset Configuration
    dataset_path: str = "./dataset/Phishing_Email.csv"
    train_split: float = 0.8
    random_seed: int = 42
    
    # OSINT Configuration
    osint_weight: float = 0.3
    ml_weight: float = 0.7
    high_risk_threshold: float = 0.8
    low_risk_threshold: float = 0.2
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
