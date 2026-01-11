"""Test to/from string modules"""

from pathlib import Path
import hwl
import random

from util import compile_manifest, send_axi_through_module


def test_top(tmp_path: Path):
    # TODO include some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence
    M = 10**5
    sample_count = 32

    c = compile_manifest()
    m: hwl.Module = c.resolve("top.top")
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]
    input_string = "\n".join(f"{x},{y}" for x, y in samples) + "\n\0"

    expected_output = max((abs(xa - xb) + 1) * (abs(ya - yb) + 1) for xa, ya in samples for xb, yb in samples)
    expected_output_str = str(expected_output) + "\n"

    max_cycles = len(input_string) + len(samples) ** 2 + 128
    output = send_axi_through_module(inst, [ord(c) for c in input_string], max_cycles=max_cycles)

    output_str = "".join(chr(c) for c in output)
    assert output_str == expected_output_str
