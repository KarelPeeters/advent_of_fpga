"""Test to/from string modules"""

from pathlib import Path
from typing import List, Optional, Tuple
import hwl
import random

from util import compile_manifest


def test_parse_points(tmp_path: Path):
    # TODO include some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence
    M = 10**5
    sample_count = 64

    c = compile_manifest()
    m: hwl.Module = c.resolve("string.parse_points")(M=M)
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]
    input_string = "\n".join(f"{x},{y}" for x, y in samples) + "\n"

    output = send_axi_through_module(inst, [ord(c) for c in input_string], max_cycles=len(input_string) + 16)
    assert output == samples


def test_int_to_chars(tmp_path: Path):
    # TODO include some edge cases, eg. 0-9, max value, ...
    M = 10**5
    sample_count = 64

    c = compile_manifest()
    m: hwl.Module = c.resolve("string.int_to_chars")(M=M)
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    values = [random.randrange(M) for _ in range(sample_count)]
    expected_output_string = "\n".join(str(v) for v in values) + "\n"

    output = send_axi_through_module(inst, values, max_cycles=2 * len(expected_output_string) + 16)
    output_string = "".join(chr(x) for x in output)
    assert output_string == expected_output_string


def send_axi_through_module(inst: hwl.VerilatedInstance, input_data: List, max_cycles: int) -> List:
    output = []

    # reset
    ports = inst.ports
    ports.rst.value = True
    inst.step(1)
    ports.rst.value = False
    inst.step(1)

    # clock loop
    for i in range(max_cycles):
        ports.clk.value = True
        inst.step(1)
        ports.clk.value = False
        inst.step(1)

        # handle precious input handshake
        if ports.input_valid.value and ports.input_ready.value:
            ports.input_valid.value = False

        # send input
        if not ports.input_valid.value and input_data:
            ports.input_valid.value = True
            ports.input_data.value = input_data[0]
            input_data = input_data[1:]

        # handle output handshake, collect output
        if ports.output_valid.value and ports.output_ready.value:
            output.append(ports.output_data.value)
        ports.output_ready.value = True

    # assert not input_data, "Failed to send all input"
    return output
