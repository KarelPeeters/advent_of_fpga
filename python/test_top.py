"""Test to/from string modules"""

from pathlib import Path
from typing import List, Tuple
import hwl
import random

from util import EXTRA_VERILOG_FILES, compile_manifest, send_axi_through_module


def test_top_empty(tmp_path: Path):
    inst = top_instance(tmp_path)
    assert run_and_check_top(inst, []) == 0


def test_top_single(tmp_path: Path):
    inst = top_instance(tmp_path)
    assert run_and_check_top(inst, [(16, 32)]) == 1


def test_top_double(tmp_path: Path):
    inst = top_instance(tmp_path)
    assert run_and_check_top(inst, [(16, 32), (20, 30)]) == 15


# TODO test some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence
def test_top_random(tmp_path: Path):
    M = 10**5
    sample_count = 64

    random.seed(0x42)
    samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]

    inst = top_instance(tmp_path)
    run_and_check_top(inst, samples)


def run_and_check_top(inst: hwl.VerilatedInstance, samples: List[Tuple[int, int]]) -> int:
    # TODO include some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence

    input_string = "".join(f"{x},{y}\n" for x, y in samples) + "\0"

    expected_output = max(
        ((abs(xa - xb) + 1) * (abs(ya - yb) + 1) for xa, ya in samples for xb, yb in samples),
        default=0,
    )
    expected_output_str = str(expected_output) + "\n"

    max_cycles = len(input_string) + len(samples) ** 2 // 2 + 1024
    output = send_axi_through_module(inst, [ord(c) for c in input_string], max_cycles=max_cycles)

    output_str = "".join(chr(c) for c in output)
    assert output_str == expected_output_str

    return int(output_str.strip())


def top_instance(tmp_path: Path) -> hwl.VerilatedInstance:
    c = compile_manifest()
    m: hwl.Module = c.resolve("top.top")
    return m.as_verilated(tmp_path, extra_verilog_files=EXTRA_VERILOG_FILES).instance()
