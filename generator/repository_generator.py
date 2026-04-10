# 파일 경로: generator/repository_generator.py

import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name


class RepositoryGenerator:
    def __init__(self, config):
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self, table_meta):
        entity_name = to_entity_name(table_meta.name)
        module_name = table_meta.name.split('_')[0]

        # 템플릿 목록
        targets = [
            ('common/repository/repository.java.j2', f"{entity_name}Repository.java"),
            ('common/repository/repository_custom.java.j2', f"{entity_name}RepositoryCustom.java"),
            ('common/repository/repository_impl.java.j2', f"{entity_name}RepositoryImpl.java"),
        ]

        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'repository'
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = []
        for tpl_path, file_name in targets:
            template = self.env.get_template(tpl_path)
            content = template.render(
                base_package=self.config.base_package,
                module_name=module_name,
                entity_name=entity_name
            )

            full_path = os.path.join(output_dir, file_name)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            generated_files.append(full_path)

        return generated_files