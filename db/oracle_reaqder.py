import oracledb
from .base_reader import BaseDbReader, TableMeta, ColumnMeta


class OracleReader(BaseDbReader):
    def __init__(self, config):
        super().__init__(config)
        self.conn = None
        # 오라클은 스키마(사용자명)와 테이블명이 기본적으로 대문자로 저장됩니다.
        self.schema = self.schema.upper() if self.schema else None

    def connect(self):
        db_config = self.config.db_config
        try:
            # oracledb thin 모드 (별도의 오라클 클라이언트 설치 불필요)
            # 포트와 데이터베이스명(SID/Service Name) 조합
            dsn_str = f"{db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}"
            self.conn = oracledb.connect(
                user=db_config.get('user'),
                password=db_config.get('password'),
                dsn=dsn_str
            )
        except Exception as e:
            print(f"DEBUG - 오라클 DB 접속 실패: {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

    def get_tables(self, target_tables=None):
        if not self.conn:
            self.connect()

        tables = []
        cursor = self.conn.cursor()

        # ALL_TAB_COMMENTS 쿼리를 통해 테이블 목록과 코멘트 조회
        table_query = """
                      SELECT TABLE_NAME, COMMENTS
                      FROM ALL_TAB_COMMENTS
                      WHERE OWNER = :schema \
                        AND TABLE_TYPE = 'TABLE'
                      """
        cursor.execute(table_query, schema=self.schema)

        # target_tables가 있을 경우 대소문자 구분 없이 비교하기 위해 대문자로 변환
        upper_targets = [t.upper() for t in target_tables] if target_tables else []

        for row in cursor.fetchall():
            table_name, table_comment = row[0], row[1]

            if upper_targets and table_name not in upper_targets:
                continue

            # 다른 시스템(Postgres 등)과 생성 호환성을 맞추기 위해 테이블명을 소문자로 변환하여 저장
            table_meta = TableMeta(name=table_name.lower(), comment=table_comment)
            table_meta.columns = self._get_columns(cursor, table_name)
            tables.append(table_meta)

        cursor.close()
        return tables

    def _get_columns(self, cursor, table_name):
        column_query = """
                       SELECT c.COLUMN_NAME, \
                              c.DATA_TYPE, \
                              c.NULLABLE, \
                              cc.COMMENTS, \
                              CASE WHEN cons.CONSTRAINT_TYPE = 'P' THEN 1 ELSE 0 END as IS_PK
                       FROM ALL_TAB_COLUMNS c
                                LEFT JOIN ALL_COL_COMMENTS cc
                                          ON c.OWNER = cc.OWNER AND c.TABLE_NAME = cc.TABLE_NAME AND \
                                             c.COLUMN_NAME = cc.COLUMN_NAME
                                LEFT JOIN (SELECT cols.COLUMN_NAME, c.CONSTRAINT_TYPE, c.OWNER, c.TABLE_NAME \
                                           FROM ALL_CONSTRAINTS c \
                                                    JOIN ALL_CONS_COLUMNS cols \
                                                         ON c.CONSTRAINT_NAME = cols.CONSTRAINT_NAME AND c.OWNER = cols.OWNER \
                                           WHERE c.CONSTRAINT_TYPE = 'P') cons
                                          ON c.OWNER = cons.OWNER AND c.TABLE_NAME = cons.TABLE_NAME AND \
                                             c.COLUMN_NAME = cons.COLUMN_NAME
                       WHERE c.OWNER = :schema
                         AND c.TABLE_NAME = :table_name
                       ORDER BY c.COLUMN_ID
                       """
        cursor.execute(column_query, schema=self.schema, table_name=table_name)

        columns = []
        for r in cursor.fetchall():
            # 컬럼명도 소문자로 변환 (name_util.py 호환을 위함)
            col_name = r[0].lower()
            data_type = r[1].split('(')[0]  # VARCHAR2(50) -> VARCHAR2
            is_nullable = True if r[2] == 'Y' else False
            comment = r[3]
            is_pk = True if r[4] == 1 else False

            columns.append(ColumnMeta(
                name=col_name,
                data_type=data_type,
                is_nullable=is_nullable,
                comment=comment,
                is_pk=is_pk
            ))
        return columns