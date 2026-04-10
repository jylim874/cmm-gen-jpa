# 파일 경로: generator/type_mapper.py

def map_db_type_to_java(db_type: str) -> str:
    """PostgreSQL 타입을 Java 타입으로 매핑"""
    db_type = db_type.lower()

    mapping = {
        'bigint': 'Long',
        'int8': 'Long',
        'bigserial': 'Long',
        'integer': 'Integer',
        'int4': 'Integer',
        'smallint': 'Integer',
        'character varying': 'String',
        'varchar': 'String',
        'text': 'String',
        'boolean': 'Boolean',
        'bool': 'Boolean',
        'timestamp': 'OffsetDateTime',
        'timestamptz': 'OffsetDateTime',
        'timestamp with time zone': 'OffsetDateTime',
        'date': 'LocalDate',
        'numeric': 'BigDecimal',
        'decimal': 'BigDecimal',
        'double precision': 'Double',
        'float8': 'Double'
    }

    return mapping.get(db_type, 'String')  # 매핑 없으면 기본 String