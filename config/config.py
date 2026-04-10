import yaml
import os
import glob

class Config:
    def __init__(self, config_path='config/settings.yaml'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, config_path)

        # 1. 기본 settings.yaml 로드 (인코딩 안전 처리)
        try:
            with open(full_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                self.raw_config = yaml.safe_load(f)
        except Exception:
            with open(full_path, 'r', encoding='cp949', errors='ignore') as f:
                self.raw_config = yaml.safe_load(f)

        self.project = self.raw_config.get('project', {})
        self.db_config = self.raw_config.get('db_config', {})
        self.run = self.raw_config.get('run', {})
        self.rules = self.raw_config.get('generator_rules', {})

        # 🔍 속성 직접 정의 (이 부분이 누락되면 AttributeError가 발생합니다)
        self.schema = self.run.get('schema', 'public')
        self.target_tables = self.run.get('target_tables', [])  # 이 줄을 꼭 추가하세요!

        # DB 타입 검증
        self.db_type = self.db_config.get('type', 'postgresql').lower()

        # 도메인 매핑 자동 로드
        self.project['domain_mapping'] = self._load_domain_mappings()

    def _load_domain_mappings(self):
        domain_mapping = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # domains 폴더 내 모든 yaml 파일 읽기
        domain_files = glob.glob(os.path.join(base_dir, 'config', 'domains', '*.yaml'))

        for file_path in domain_files:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    data = yaml.safe_load(f)
                    if data:
                        domain_mapping.update(data)
            except Exception as e:
                print(f"⚠️ 도메인 파일 로드 실패 ({file_path}): {e}")

        return domain_mapping

    @property
    def base_package(self): return self.project.get('base_package')

    @property
    def audit_columns(self): return self.rules.get('audit_columns', [])