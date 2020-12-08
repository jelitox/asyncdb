from typing import Any, List, Optional, get_type_hints, Callable, ClassVar, Union
from asyncdb.utils.models import Model, Column


f = [
    ('sara_order_no', str),
    ('dealer_name', str),
    ('dealer_code', str),
    ('retailer', str),
    ('store_no', int)
]

act = Model.make_model(name='activity_data', schema='att', fields=f)
m = act()
print(m.schema(type='sql'))
