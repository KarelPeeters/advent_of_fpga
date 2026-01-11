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
