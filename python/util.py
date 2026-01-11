from pathlib import Path
from typing import List
import hwl


def compile_manifest() -> hwl.Compile:
    manifest = Path(__file__).parent / "../rtl/hwl.toml"
    source = hwl.Source.new_from_manifest_path(str(manifest))
    return source.compile()


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

    assert input_data == [], "Failed to send all input"
    return output
