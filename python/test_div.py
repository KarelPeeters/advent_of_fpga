import hwl
import random

from util import compile_manifest


def test_div() -> None:
    c = compile_manifest()
    f: hwl.Function = c.resolve("div.div_by_const")

    random.seed(0x42)
    for _ in range(128):
        m = random.randrange(2**24)
        a = random.randrange(m)
        b = random.randrange(m * 2)
        assert f(m, a, b) == a // b
