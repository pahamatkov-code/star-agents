from .config import BaseConfig

class ProdSettings(BaseConfig):
    class Config:
        env_file = ".env.production"
