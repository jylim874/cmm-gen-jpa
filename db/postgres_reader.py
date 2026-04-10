import pg8000
from .base_reader import BaseDbReader, TableMeta, ColumnMeta


class PostgresReader(BaseDbReader):
    def __init__(self, config):
        super().__init__(config)
        self.conn = None  # 초기값 설정 (AttributeError 방지)

    def connect(self):
        db_config = self.config.db_config
        try:
            # pg8000 접속
            self.conn = pg8000.connect(
                host=db_config.get('host'),
                port=int(db_config.get('port')),
                database=db_config.get('database'),  # 여기가 "portal"인지 다시 확인!
                user=db_config.get('user'),
                password=db_config.get('password')
            )
        except Exception as e:
            print(f"DEBUG - DB 접속 실패: {e}")
            raise e

    def close(self):
        if self.conn:
            self.conn.close()

    def get_tables(self, target_tables=None):
        if not self.conn:
            self.connect()

        tables = []
        cursor = self.conn.cursor()

        # pg8000 쿼리 파라미터는 %s를 지원합니다.
        table_query = """
                      SELECT c.relname, obj_description(c.oid)
                      FROM pg_class c
                               JOIN pg_namespace n ON n.oid = c.relnamespace
                      WHERE c.relkind IN ('r', 'p') \
                        AND n.nspname = %s \
                      """
        cursor.execute(table_query, (self.schema,))

        for row in cursor.fetchall():
            table_name, table_comment = row[0], row[1]
            if target_tables and table_name not in target_tables:
                continue

            table_meta = TableMeta(name=table_name, comment=table_comment)
            table_meta.columns = self._get_columns(cursor, table_name)
            tables.append(table_meta)

        cursor.close()
        return tables

    def _get_columns(self, cursor, table_name):
        column_query = """
                       SELECT a.attname, \
                              pg_catalog.format_type(a.atttypid, a.atttypmod),
                              not a.attnotnull, \
                              col_description(a.attrelid, a.attnum),
                              coalesce(i.indisprimary, false)
                       FROM pg_catalog.pg_attribute a
                                JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                                JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                                LEFT JOIN pg_index i \
                                          ON i.indrelid = c.oid AND a.attnum = any (i.indkey) AND i.indisprimary
                       WHERE c.relname = %s \
                         AND n.nspname = %s \
                         AND a.attnum > 0 \
                         AND not a.attisdropped
                       ORDER BY a.attnum; \
                       """
        cursor.execute(column_query, (table_name, self.schema))

        columns = []
        for r in cursor.fetchall():
            columns.append(ColumnMeta(
                name=r[0],
                data_type=r[1].split('(')[0],
                is_nullable=r[2],
                comment=r[3],
                is_pk=r[4]
            ))
        return columns