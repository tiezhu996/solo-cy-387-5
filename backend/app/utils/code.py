import secrets


def generate_pickup_code(length: int = 6) -> str:
    """生成数字取件凭证（默认 6 位，不足补零）。"""
    upper = 10 ** length
    return f'{secrets.randbelow(upper):0{length}d}'
