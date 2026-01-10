"""Test to/from string modules"""

from pathlib import Path
from typing import List, Optional, Tuple
import hwl
import random

from util import compile_manifest


# TODO extract common axi in/out test infrastructure
def test_parse(tmp_path: Path):
    M = 10**5
    sample_count = 64

    c = compile_manifest()
    m: hwl.Module = c.resolve("string.parse")(M=M)
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    samples = [(random.randrange(M), random.randrange(M)) for _ in range(sample_count)]
    input_string = "\n".join(f"{x},{y}" for x, y in samples) + "\n"

    input_remaining: str = input_string
    output_received: List[Tuple[int, int]] = []

    # reset
    ports = inst.ports
    ports.rst.value = True
    inst.step(1)
    ports.rst.value = False
    inst.step(1)

    # clock loop
    for i in range(len(input_string) + 16):
        ports.clk.value = True
        inst.step(1)
        ports.clk.value = False
        inst.step(1)

        # handle precious input handshake
        if ports.input_valid.value and ports.input_ready.value:
            ports.input_valid.value = False

        # send input, with trailing zero to signal end
        if not ports.input_valid.value and input_remaining:
            ports.input_valid.value = True
            ports.input_data.value = ord(input_remaining[0])
            input_remaining = input_remaining[1:]

        # handle output handshake, collect output
        if ports.output_valid.value and ports.output_ready.value:
            output_received.append(ports.output_data.value)
        ports.output_ready.value = True

    assert input_remaining == "", "Failed to send all input"
    assert output_received == samples, "Incorrect output"
