from pathlib import Path
from typing import Any, List, Optional
import hwl

EXTRA_VERILOG_FILES = [
    Path(__file__).parent / "../rtl/xilinx_uram.v",
]


def compile_manifest() -> hwl.Compile:
    manifest = Path(__file__).parent / "../rtl/hwl.toml"
    source = hwl.Source.new_from_manifest_path(str(manifest))
    return source.compile()


def send_axi_through_module(
    inst: hwl.VerilatedInstance, input_data: List, max_cycles: int, output_end: Optional[Any] = None
) -> List:
    output: List = []

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

            if not input_data:
                print(f"Last input sent at cycle {i}")

        # handle output handshake, collect output
        if ports.output_valid.value and ports.output_ready.value:
            if not output:
                print(f"First output received at cycle {i}")

            output_value = ports.output_data.value
            output.append(output_value)

            if output_end is not None and output_value == output_end:
                print(f"Output end {output_end} received at cycle {i}")
                break

        ports.output_ready.value = True

    assert input_data == [], "Failed to send all input"
    return output
