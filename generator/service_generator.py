import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name, get_module_name


class ServiceGenerator:
    def __init__(self, config):
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self, table_meta):
        entity_name = to_entity_name(table_meta.name)

        # settings.yaml의 domain_mapping 정보를 사용하여 모듈명 결정
        domain_mapping = self.config.project.get('domain_mapping', {})
        module_name = get_module_name(table_meta.name, domain_mapping)

        targets = [
            ('common/service/service.java.j2', f"{entity_name}Service.java"),
            ('common/service/service_impl.java.j2', f"{entity_name}ServiceImpl.java")
        ]

        # 물리적 저장 경로 설정
        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'service'
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for tpl_path, file_name in targets:
            template = self.env.get_template(tpl_path)
            content = template.render(
                base_package=self.config.base_package,
                module_name=module_name,
                entity_name=entity_name
            )

            file_path = os.path.join(output_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return output_dir