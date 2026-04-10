# 파일 경로: config/config_loader.py

import os
import yaml


class Config:
    def __init__(self, config_dict: dict):
        self.project = config_dict.get('project', {})
        self.base_package = self.project.get('base_package', 'com.example')

        self.db_config = config_dict.get('db_config', {})
        # db_type을 소문자로 통일해서 저장
        self.db_type = self.db_config.get('type', 'postgresql').lower()

        # 지원하는 DB 타입인지 검증
        valid_db_types = ['postgresql', 'oracle', 'mysql', 'mariadb']
        if self.db_type not in valid_db_types:
            raise ValueError(f"지원하지 않는 DB 타입입니다: {self.db_type}. 지원 목록: {valid_db_types}")

        self.generator_rules = config_dict.get('generator_rules', {})

        self.run = config_dict.get('run', {})
        self.schema = self.run.get('schema', 'public')
        self.target_tables = self.run.get('target_tables', [])

    @property
    def audit_columns(self) -> list:
        return self.generator_rules.get('audit_columns', [])


def load_config(config_path: str = "config/settings.yaml") -> Config:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, config_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {full_path}")

    # 인코딩 에러를 방지하기 위해 utf-8-sig와 errors='ignore'를 조합합니다.
    try:
        with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            config_dict = yaml.safe_load(f)
    except UnicodeDecodeError:
        # 만약 그래도 안 된다면 윈도우 기본 인코딩(cp949)으로 한 번 더 시도합니다.
        with open(full_path, 'r', encoding='cp949', errors='ignore') as f:
            config_dict = yaml.safe_load(f)

    return Config(config_dict)