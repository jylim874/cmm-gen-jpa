# 파일 경로: utils/name_util.py

def to_pascal_case(snake_str: str) -> str:
    """snake_case -> PascalCase (예: user_account -> UserAccount)"""
    if not snake_str:
        return ""
    return "".join(word.capitalize() for word in snake_str.lower().split("_"))

def to_camel_case(snake_str: str) -> str:
    """snake_case -> camelCase (예: user_account -> userAccount)"""
    if not snake_str:
        return ""
    words = snake_str.lower().split("_")
    if len(words) == 1:
        return words[0]
    return words[0] + "".join(word.capitalize() for word in words[1:])

def to_entity_name(table_name: str) -> str:
    """테이블명 -> 엔티티 클래스명 (예: user_role_map -> UserRoleMap)"""
    return to_pascal_case(table_name)

def get_module_name(table_name, domain_mapping):
    """테이블명이 속한 도메인(모듈) 명을 반환합니다."""
    # print("DOMAIN_MAPPING:", domain_mapping)

    for module, tables in domain_mapping.items():
        if table_name in tables:
            return module
    return table_name.split('_')[0]  # 매핑 없으면 첫 단어 사용