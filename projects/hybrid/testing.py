import json
import os

import pandas as pd


def random(z):
    """[summary]

    Parameters
    ----------
    z : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    x = 10 * z
    y = 20 * z
    return x ** y


def random2():
    """Second Random Doc."""
    k = '{"1": "2", "3": "4"}'
    for key, value in json.loads(k).items():
        print(f"{int(key)} = {int(value)}")


if __name__ == "__main__":
    random2()
