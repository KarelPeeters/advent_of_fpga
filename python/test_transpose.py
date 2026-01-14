from pathlib import Path
import hwl
import pytest
from util import compile_manifest


@pytest.mark.parametrize("N", range(4))
def test_transpose(N: int, tmp_path: Path):
    c = compile_manifest()

    T = c.resolve("std.types.uint")(8)

    m: hwl.Module = c.resolve("transpose.transpose")(N=N, T=T)

    inst = m.as_verilated(tmp_path).instance()
    ports = inst.ports

    ports.rst.value = True
    inst.step(1)
    ports.rst.value = False
    inst.step(1)

    B = 3
    cycles = 4 if N <= 1 else (B + 1) * N

    input_shaped = [[[b * N * N + j * N + i for i in range(N)] for j in range(N)] for b in range(B)]
    output_shapes = [[[input_shaped[b][i][j] for i in range(N)] for j in range(N)] for b in range(B)]

    input_flat = [line for block in input_shaped for line in block]
    output_flat = [line for block in output_shapes for line in block]

    first_output_cycle = N

    for i in range(cycles):
        if i < len(input_flat):
            ports.data_in.value = input_flat[i]

        ports.clk.value = True
        inst.step(1)
        ports.clk.value = False
        inst.step(1)

        if i >= first_output_cycle:
            expected = output_flat[i - first_output_cycle] if N != 0 else []
            assert ports.data_out.value == expected
