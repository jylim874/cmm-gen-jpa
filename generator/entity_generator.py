import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name, to_camel_case, get_module_name
from .type_mapper import map_db_type_to_java

class EntityGenerator:
    def __init__(self, config):
        self.config = config
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_path))

    def generate(self, table_meta):
        entity_name = to_entity_name(table_meta.name)
        # domain_mapping 적용
        domain_mapping = self.config.project.get('domain_mapping', {})
        module_name = get_module_name(table_meta.name, domain_mapping)

        audit_cols = self.config.audit_columns
        fields = []
        for col in table_meta.columns:
            if col.name in audit_cols: continue
            fields.append({
                'name': col.name,
                'field_name': to_camel_case(col.name),
                'type': map_db_type_to_java(col.data_type),
                'is_pk': col.is_pk,
                'is_nullable': col.is_nullable,
                'comment': col.comment
            })

        template = self.env.get_template('common/entity/entity.java.j2')
        content = template.render(
            base_package=self.config.base_package,
            common_package=self.config.project.get('common_package'),
            module_name=module_name, # 추가
            table_name=table_meta.name,
            entity_name=entity_name,
            table_comment=table_meta.comment,
            fields=fields
        )

        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'entity'
        )
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        file_path = os.path.join(output_dir, f"{entity_name}.java")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path