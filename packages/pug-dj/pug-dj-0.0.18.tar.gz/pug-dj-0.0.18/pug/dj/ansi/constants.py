"""
ansi.constants

>>> FIELD_TYPE_NUM.CHARACTER_VARYING
12
>>> FIELD_TYPE_NUM.REAL
7
>>> field_type_name[FIELD_TYPE_NUM.TIMESTAMP]
'TIMESTAMP'
>>> reverse_field_type_name['FLOAT']
6
"""

class FIELD_TYPE_NUM:
    BLOB = 30
    BOOLEAN = 16
    CHARACTER = 1
    CHARACTER_VARYING = 12
    CLOB = 40
    DATE = 91
    TIME = 92
    TIMESTAMP = 93
    DECIMAL = 3
    DOUBLE_PRECISION = 8
    FLOAT = 6
    INTEGER = 4
    NUMERIC = 2
    REAL = 7
    SMALLINT = 5


field_type_name = dict(
    (getattr(FIELD_TYPE_NUM, name, ''), name) for name in dir(FIELD_TYPE_NUM) if not name.startswith('_')
    )

reverse_field_type_name = dict(
    (name, getattr(FIELD_TYPE_NUM, name, '')) for name in dir(FIELD_TYPE_NUM) if not name.startswith('_')
    )
