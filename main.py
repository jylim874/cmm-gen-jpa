# 파일 경로: main.py

import os
from config import load_config
from db.postgres_reader import PostgresReader
from generator.dto_generator import DtoGenerator
from generator.entity_generator import EntityGenerator
from generator.repository_generator import RepositoryGenerator # 상단에 추가


def main():
    try:
        # 1. 설정 로드
        print("🚀 [1/4] 설정을 로드하는 중...")
        config = load_config()

        # 2. DB 접속
        print(f"🔗 [2/4] {config.db_type} 데이터베이스 접속 시도...")
        reader = PostgresReader(config)
        reader.connect()

        # 3. 테이블 및 컬럼 정보 추출
        print(f"📂 [3/4] '{config.schema}' 스키마에서 메타데이터를 추출하는 중...")
        tables = reader.get_tables(target_tables=config.target_tables)

        if not tables:
            print(f"⚠️  '{config.schema}' 스키마에 테이블이 없거나 설정을 확인해 주세요.")
            return

        # 4. 코드 생성기 초기화 및 실행
        print(f"🛠️  [4/4] 총 {len(tables)}개 테이블에 대한 Java 파일 생성을 시작합니다.")
        entity_gen = EntityGenerator(config)
        repo_gen = RepositoryGenerator(config)  # 4단계 시작 부분에 추가
        dto_gen = DtoGenerator(config)

        for table in tables:
            try:
                # Entity 생성 실행
                file_path = entity_gen.generate(table)
                # Repository 생성 추가
                repo_gen.generate(table)
                dto_gen.generate(table)

                print(f" ✅ 생성 완료: {table.name} -> {os.path.basename(file_path)}")


            except Exception as gen_e:
                print(f" ❌ 테이블 '{table.name}' 생성 중 오류: {gen_e}")

        print("\n✨ 모든 작업이 완료되었습니다!")
        print(f"📍 출력 경로: {config.project.get('home')}")

    except Exception as e:
        print(f"\n🚨 실행 중 치명적 오류 발생: {e}")
    finally:
        if 'reader' in locals() and hasattr(reader, 'conn') and reader.conn:
            reader.close()


if __name__ == "__main__":
    main()