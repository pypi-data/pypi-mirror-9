from __future__ import absolute_import, division, print_function

from into.backends.pandas import discover
import pandas as pd
from datashape import dshape
from into import into, append, convert, resource, discover

data = [('Alice', 100), ('Bob', 200)]

def test_discover_dataframe():
    df = pd.DataFrame([('Alice', 100), ('Bob', 200)],
                        columns=['name', 'amount'])

    assert discover(df) == dshape('2 * {name: string, amount: int64}')


def test_discover_series():
    s = pd.Series([1, 2, 3])

    assert discover(s) == 3 * discover(s[0])
