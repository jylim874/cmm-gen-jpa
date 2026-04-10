# 파일 경로: db/base_reader.py

from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod


@dataclass
class ColumnMeta:
    """DB 컬럼 원본 정보를 담는 데이터 클래스"""
    name: str  # DB 컬럼명 (예: user_account_id)
    data_type: str  # DB 데이터 타입 (예: varchar, bigint)
    is_nullable: bool  # Null 허용 여부
    is_pk: bool  # Primary Key 여부
    comment: Optional[str]  # 컬럼 코멘트 (Swagger/Javadoc 용도)


@dataclass
class TableMeta:
    """DB 테이블 원본 정보를 담는 데이터 클래스"""
    name: str  # DB 테이블명 (예: user_role_map)
    comment: Optional[str]  # 테이블 코멘트
    columns: List[ColumnMeta] = field(default_factory=list)


class BaseDbReader(ABC):
    """모든 DB Reader가 상속받아야 하는 추상 클래스"""

    def __init__(self, config):
        self.config = config
        self.schema = config.run.get('schema', 'public')

    @abstractmethod
    def connect(self):
        """DB 접속"""
        pass

    @abstractmethod
    def close(self):
        """DB 접속 해제"""
        pass

    @abstractmethod
    def get_tables(self, target_tables: List[str] = None) -> List[TableMeta]:
        """테이블 목록과 각 테이블의 컬럼 정보를 읽어옴"""
        pass