import math
from pathlib import Path
import hwl
import random

from util import compile_manifest, send_axi_through_module


def test_parse_points(tmp_path: Path):
    # TODO include some edge cases, eg. 0,0, max values, or a bunch of short pairs in sequence
    M = 10**5
    sample_count = 64

    c = compile_manifest()
    m: hwl.Module = c.resolve("string.parse_points")(M=M)
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    expected_output = []
    input_string = ""
    any_zero = False

    for i in range(sample_count):
        if i % 20 == 0:
            expected_output.append((False, (0, 0)))
            input_string += "\0"
            any_zero = True
        else:
            x = random.randrange(M)
            y = random.randrange(M)
            expected_output.append((True, (x, y)))
            input_string += f"{x},{y}\n"
    assert any_zero, "Test data should include at least one zero point"

    output = send_axi_through_module(inst, [ord(c) for c in input_string], max_cycles=len(input_string) + 16)
    assert output == expected_output


def test_int_to_chars(tmp_path: Path):
    # TODO include some edge cases, eg. 0-9, max value, ...
    M = 10**5
    sample_count = 64

    c = compile_manifest()
    m: hwl.Module = c.resolve("string.int_to_chars")(M=M)
    inst = m.as_verilated(tmp_path).instance()

    random.seed(0x42)
    values = list(range(20)) + [random.randrange(M) for _ in range(sample_count)]
    expected_output_string = "\n".join(str(v) for v in values) + "\n"

    max_cycles = 2 * math.ceil(math.log2(M)) * len(expected_output_string) + 16
    output = send_axi_through_module(inst, values, max_cycles=max_cycles)
    output_string = "".join(chr(x) for x in output)
    assert output_string == expected_output_string
