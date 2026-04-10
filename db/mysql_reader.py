import pymysql
from .base_reader import BaseDbReader, TableMeta, ColumnMeta


class MysqlReader(BaseDbReader):
    def __init__(self, config):
        super().__init__(config)
        self.conn = None

    def connect(self):
        db_config = self.config.db_config
        try:
            # pymysql 접속
            self.conn = pymysql.connect(
                host=db_config.get('host'),
                port=int(db_config.get('port', 3306)),
                user=db_config.get('user'),
                password=db_config.get('password'),
                database=db_config.get('database'),
                charset='utf8mb4'  # 이모지 등 다국어 처리 지원
            )
        except Exception as e:
            print(f"DEBUG - MySQL/MariaDB 접속 실패: {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

    def get_tables(self, target_tables=None):
        if not self.conn:
            self.connect()

        tables = []
        with self.conn.cursor() as cursor:
            # information_schema.TABLES 조회
            table_query = """
                          SELECT TABLE_NAME, TABLE_COMMENT
                          FROM information_schema.TABLES
                          WHERE TABLE_SCHEMA = %s \
                            AND TABLE_TYPE = 'BASE TABLE'
                          """
            cursor.execute(table_query, (self.schema,))

            for row in cursor.fetchall():
                table_name, table_comment = row[0], row[1]

                if target_tables and table_name not in target_tables:
                    continue

                table_meta = TableMeta(name=table_name, comment=table_comment)
                table_meta.columns = self._get_columns(table_name)
                tables.append(table_meta)

        return tables

    def _get_columns(self, table_name):
        columns = []
        with self.conn.cursor() as cursor:
            # information_schema.COLUMNS 조회
            column_query = """
                           SELECT COLUMN_NAME,
                                  DATA_TYPE,
                                  IS_NULLABLE,
                                  COLUMN_COMMENT,
                                  COLUMN_KEY
                           FROM information_schema.COLUMNS
                           WHERE TABLE_SCHEMA = %s \
                             AND TABLE_NAME = %s
                           ORDER BY ORDINAL_POSITION
                           """
            cursor.execute(column_query, (self.schema, table_name))

            for r in cursor.fetchall():
                # MySQL의 IS_NULLABLE은 'YES' 또는 'NO', COLUMN_KEY는 'PRI' 등으로 반환됩니다.
                is_nullable = True if r[2] == 'YES' else False
                is_pk = True if r[4] == 'PRI' else False

                columns.append(ColumnMeta(
                    name=r[0],
                    data_type=r[1].lower(),  # 타입은 소문자로 통일하여 type_mapper와 호환되게 함
                    is_nullable=is_nullable,
                    comment=r[3],
                    is_pk=is_pk
                ))

        return columns