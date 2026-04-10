# 파일 경로: generator/entity_generator.py

import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name, to_camel_case
from .type_mapper import map_db_type_to_java


class EntityGenerator:
    def __init__(self, config):
        self.config = config
        # templates 폴더 위치 설정
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_path))

    def generate(self, table_meta):
        # 1. 템플릿 로드
        template = self.env.get_template('common/entity/entity.java.j2')

        # 2. 렌더링에 필요한 데이터 준비
        entity_name = to_entity_name(table_meta.name)

        # BaseEntity에 이미 있는 컬럼은 제외 (audit_columns 설정 활용)
        audit_cols = self.config.audit_columns
        fields = []
        for col in table_meta.columns:
            if col.name in audit_cols:
                continue

            fields.append({
                'name': col.name,
                'field_name': to_camel_case(col.name),
                'type': map_db_type_to_java(col.data_type),
                'is_pk': col.is_pk,
                'is_nullable': col.is_nullable,
                'comment': col.comment
            })

        # 3. 데이터 바인딩
        content = template.render(
            base_package=self.config.base_package,
            common_package=self.config.project.get('common_package'),
            table_name=table_meta.name,
            entity_name=entity_name,
            table_comment=table_meta.comment,
            fields=fields
        )

        # 4. 파일 저장 경로 설정 (api/테이블명/entity/Entity.java)
        # 테이블명에서 모듈명을 추출하는 로직은 프로젝트 규칙에 따라 조정 가능합니다.
        # 여기서는 단순하게 테이블명을 모듈 폴더명으로 사용합니다.
        module_name = table_meta.name.split('_')[0]
        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'entity'
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, f"{entity_name}.java")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path