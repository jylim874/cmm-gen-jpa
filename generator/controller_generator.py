import os
from jinja2 import Environment, FileSystemLoader
from utils.name_util import to_entity_name, get_module_name


class ControllerGenerator:
    def __init__(self, config):
        self.config = config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate(self, table_meta):
        entity_name = to_entity_name(table_meta.name)

        domain_mapping = self.config.project.get('domain_mapping', {})
        module_name = get_module_name(table_meta.name, domain_mapping)

        template = self.env.get_template('common/controller/controller.java.j2')
        content = template.render(
            base_package=self.config.base_package,
            module_name=module_name,
            entity_name=entity_name
        )

        output_dir = os.path.join(
            self.config.project.get('home'),
            'src/main/java',
            self.config.base_package.replace('.', '/'),
            module_name,
            'controller'
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, f"{entity_name}Controller.java")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path