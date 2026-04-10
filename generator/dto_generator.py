# 파일 경로: generator/dto_generator.py

import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name, to_camel_case
from .type_mapper import map_db_type_to_java


class DtoGenerator:
    def __init__(self, config):
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self, table_meta):
        entity_name = to_entity_name(table_meta.name)
        module_name = table_meta.name.split('_')[0]

        # 필드 추출 (Request용은 PK 제외, Response용은 포함 등 자유롭게 조절 가능)
        fields = []
        for col in table_meta.columns:
            fields.append({
                'field_name': to_camel_case(col.name),
                'type': map_db_type_to_java(col.data_type),
                'is_pk': col.is_pk,
                'is_nullable': col.is_nullable,
                'comment': col.comment
            })

        targets = [
            ('common/dto/dto_request.java.j2', f"{entity_name}Request.java"),
            ('common/dto/dto_response.java.j2', f"{entity_name}Response.java")
        ]

        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'dto'
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for tpl_path, file_name in targets:
            template = self.env.get_template(tpl_path)
            content = template.render(
                base_package=self.config.base_package,
                module_name=module_name,
                entity_name=entity_name,
                fields=fields
            )
            with open(os.path.join(output_dir, file_name), 'w', encoding='utf-8') as f:
                f.write(content)