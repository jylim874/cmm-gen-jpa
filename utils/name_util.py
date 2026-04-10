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