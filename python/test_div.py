import hwl
import random

from util import compile_manifest


def test_div_simple() -> None:
    c = compile_manifest()

    div_by_const: hwl.Function = c.resolve("div.div_by_const")

    random.seed(0x42)
    for _ in range(128):
        m = random.randrange(1, 2 ** random.randrange(1, 24))
        a = random.randrange(m)
        b = random.randrange(1, m * 2)

        assert div_by_const(m, a, b) == a // b


def test_div_pipelined() -> None:
    c = compile_manifest()

    compute_div_magic: hwl.Function = c.resolve("div.compute_div_magic")
    div_by_const_pipelined_0: hwl.Function = c.resolve("div.div_by_const_pipelined_0")
    div_by_const_pipelined_1: hwl.Function = c.resolve("div.div_by_const_pipelined_1")

    random.seed(0x42)
    for _ in range(128):
        m = random.randrange(1, 2 ** random.randrange(1, 24))
        a = random.randrange(m)
        b = random.randrange(1, m * 2)

        magic = compute_div_magic(m, b)
        print(magic)

        p = div_by_const_pipelined_0(magic, a)
        print(p)
        assert div_by_const_pipelined_1(magic, p) == a // b
