# 파일 경로: config/__init__.py
from .config import Config

def load_config(config_path="config/settings.yaml"):
    """설정 객체를 생성하여 반환합니다."""
    return Config(config_path)

__all__ = ['load_config', 'Config']