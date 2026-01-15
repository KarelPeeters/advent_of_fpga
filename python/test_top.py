"""Test to/from string modules"""

import math
from pathlib import Path
from typing import List, Tuple
import hwl
import random

import pytest

from util import EXTRA_VERILOG_FILES, compile_manifest, send_axi_through_module


# TODO test some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence


@pytest.mark.parametrize("core_width", [1, 2, 3])
def test_top_single(tmp_path: Path, core_width: int):
    inst = top_instance(tmp_path, core_width=core_width)
    assert run_and_check_top(inst, [(16, 32)]) == 1


@pytest.mark.parametrize("core_width", [1, 2, 3])
def test_top_double(tmp_path: Path, core_width: int):
    inst = top_instance(tmp_path, core_width=core_width)
    assert run_and_check_top(inst, [(16, 32), (20, 30)]) == 15


@pytest.mark.parametrize("core_width", [1, 2, 3])
def test_top_short(tmp_path: Path, core_width: int):
    inst = top_instance(tmp_path, core_width=core_width)

    M = 10**5
    random.seed(0x42)

    for sample_count in range(20):
        samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]
        run_and_check_top(inst, samples)


@pytest.mark.parametrize("core_width", [1, 8])
def test_top_random_long(tmp_path: Path, core_width: int):
    M = 10**5
    sample_count = 64

    random.seed(0x42)
    samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]

    inst = top_instance(tmp_path, core_width=core_width)
    run_and_check_top(inst, samples)


def run_and_check_top(inst: hwl.VerilatedInstance, samples: List[Tuple[int, int]]) -> int:
    input_string = "".join(f"{x},{y}\n" for x, y in samples) + "\0"

    expected_output = max(
        ((abs(xa - xb) + 1) * (abs(ya - yb) + 1) for xa, ya in samples for xb, yb in samples),
        default=0,
    )
    expected_output_str = str(expected_output) + "\n"

    max_cycles = 6 * len(input_string) + len(samples) ** 2 // 2 + 512
    output = send_axi_through_module(
        inst, [ord(c) for c in input_string], max_cycles=max_cycles, output_end=ord("\n")
    )

    output_str = "".join(chr(c) for c in output)
    assert output_str == expected_output_str

    return int(output_str.strip())


def top_instance(tmp_path: Path, core_width: int) -> hwl.VerilatedInstance:
    c = compile_manifest()
    m: hwl.Module = c.resolve("top.top_generic")(
        MAX_POINT_COUNT=1024,
        COORD_LIMIT=10**5,
        RAM_PIPELINE=8,
        CORE_WIDTH=core_width,
    )
    return m.as_verilated(tmp_path, extra_verilog_files=EXTRA_VERILOG_FILES).instance()
