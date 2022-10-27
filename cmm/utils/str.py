import re


def camel_case2snake_case(word: str):
    """Convert camel case to snake case"""
    prepare = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', word)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', prepare).lower()
