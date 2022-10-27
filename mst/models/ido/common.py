from typing import Dict
from mst.const import TEIIN, HIJOKIN, TEIIN_HIJOKIN_CHOICES


def get_teiin_hijokin(code:str) -> str:
    """定員・非常勤定義"""
    if not code:
        return None
    return dict(TEIIN_HIJOKIN_CHOICES).get(code[0])

def get_ido_type_code(csv_dict: Dict[str, str]) -> str:
    """異動種類コードを取得する
        俸給関係と非常勤の場合は、GRP_SEQを含まない
    """
    cteihijkb = csv_dict.get('CTEIHIJKB')
    cbunruicd = csv_dict.get('CBUNRUICD')
    grp_seq = csv_dict.get('GRP_SEQ')
    
    if cteihijkb == TEIIN and cbunruicd == '13' or cteihijkb == HIJOKIN:
        grp_seq = '00'

    return cteihijkb + cbunruicd + grp_seq
