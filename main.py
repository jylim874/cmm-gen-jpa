import sys
import os
from config import load_config
from db.postgres_reader import PostgresReader
from generator.entity_generator import EntityGenerator
from generator.repository_generator import RepositoryGenerator
from generator.dto_generator import DtoGenerator
from generator.service_generator import ServiceGenerator
from generator.controller_generator import ControllerGenerator

def main():
    try:
        print("🚀 [1/4] 설정을 로드하는 중...")
        config = load_config()

        # 🔍 도메인 매핑 로드 확인 (이 로그가 비어있으면 매핑이 안 된 것입니다)
        print("-" * 50)
        mapping = config.project.get('domain_mapping', {})
        if not mapping:
            print("⚠️  [경고] 도메인 매핑 데이터가 비어있습니다! config/domains/ 폴더를 확인하세요.")
        else:
            print(f"📍 로드된 도메인 모듈: {list(mapping.keys())}")
            for k, v in mapping.items():
                print(f"   - {k}: {v}")
        print("-" * 50)

        print(f"🔗 [2/4] DB 접속 시도 ({config.db_type})...")
        reader = PostgresReader(config)
        reader.connect()

        print(f"📂 [3/4] '{config.schema}' 스키마에서 메타데이터 추출 중...")
        tables = reader.get_tables(target_tables=config.target_tables)

        print(f"🛠️  [4/4] 총 {len(tables)}개 테이블 소스 코드 생성 시작...")
        gens = [
            EntityGenerator(config),
            RepositoryGenerator(config),
            DtoGenerator(config),
            ServiceGenerator(config),
            ControllerGenerator(config)
        ]

        for table in tables:
            for gen in gens:
                gen.generate(table)
            print(f" ✅ 생성 완료: {table.name}")

        print("\n✨ 모든 작업이 성공적으로 완료되었습니다.")

    except Exception as e:
        print(f"\n🚨 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()