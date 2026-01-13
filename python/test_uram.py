import math
from pathlib import Path
from typing import Dict, List, Optional
import hwl
import random

from util import EXTRA_VERILOG_FILES, compile_manifest


def test_uram_basic(tmp_path: Path):
    c = compile_manifest()

    N = 32
    M = 2**8
    P = 2

    T = c.resolve("std.types.uint")(hwl.Range(0, M))
    m: hwl.Module = c.resolve("xilinx_uram.uram")(N=N, T=T, P=P)
    inst = m.as_verilated(tmp_path, extra_verilog_files=EXTRA_VERILOG_FILES).instance()

    ports = inst.ports
    ports.clk.value = False
    ports.port_a_mem_enable.value = False
    ports.port_a_write_enable.value = False
    ports.port_b_mem_enable.value = False
    ports.port_b_write_enable.value = False

    ports.rst.value = True
    inst.step(1)
    ports.rst.value = False
    inst.step(1)

    random.seed(0x42)
    expected_content: Dict[int, int] = {}

    def clock(n: int = 1) -> None:
        for _ in range(n):
            ports.clk.value = True
            inst.step(1)
            ports.clk.value = False
            inst.step(1)

    clock()

    for _ in range(128):
        ports.port_a_mem_enable.value = False
        ports.port_a_write_enable.value = False
        ports.port_b_mem_enable.value = False
        ports.port_b_write_enable.value = False

        if not expected_content or random.randrange(2):
            # write
            addr = random.randrange(N)
            data = random.randrange(M)

            ports.port_a_mem_enable.value = True
            ports.port_a_write_enable.value = True
            ports.port_a_address.value = addr
            ports.port_a_write_data.value = data

            expected_content[addr] = data

            clock(1)
        else:
            # read
            addr = random.choice(list(expected_content.keys()))
            expected_data = expected_content[addr]

            ports.port_b_mem_enable.value = True
            ports.port_b_write_enable.value = False
            ports.port_b_address.value = addr

            clock(2 + P)

            read_data = ports.port_b_read_data.value
            assert read_data == expected_data, f"At address {addr}: expected {expected_data}, got {read_data}"
