"""pandas arguments: two different DataFrames and Series must not share a key."""

import pandas as pd
from speedupy.speedupy import deterministic


@deterministic
def column_totals(frame):
    return {name: int(frame[name].sum()) for name in frame.columns}


@deterministic
def doubled(series):
    return [int(v) * 2 for v in series]


def main():
    first = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
    second = pd.DataFrame({"x": [4, 5, 6], "y": [40, 50, 60]})
    print(column_totals(first))
    print(column_totals(second))
    print(doubled(pd.Series([1, 2, 3])))
    print(doubled(pd.Series([7, 8])))


if __name__ == "__main__":
    main()
