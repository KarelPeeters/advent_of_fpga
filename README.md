# Advent of FPGA

https://blog.janestreet.com/advent-of-fpga-challenge-2025/

Implementation of D09P1 (and hopefully P2 eventually).

Targeting _Zynq UltraScale+ Kria KV260_.
https://github.com/tomverbeure/kv260_bringup

# Requirements

[//]: # (TODO pin versions as submodules? and provide exact eg. venv setup instructions)

* Verilator: https://www.veripool.org/verilator/
* HwLang: https://github.com/KarelPeeters/HwLang

# Build, test, synthesis instructions

Ensure the following dependencies are installed on your system:
* `uv` (tested with 0.9.10)
* `verilator` (tested with 5.040)
* `ccache` (tested with 4.11.2) (optional, will speed up repeated test runs)

The compiler for the RTL language used is included in this repository as a git submodule and does not need to be installed separately.

To setup the project and install the necessary dependencies:

```
git clone --recurse-submodules https://github.com/KarelPeeters/advent_of_fpga
uv sync
```

To run tests:

```
uv run pytest -n 4 -v
```

To compile the top-level design to Verilog:

```
uv run python/compile.py
```

The output is written to `output/top.v`. Design parameters can be adjusted in `python/compile.py`.

To then synthesize the design in Vivado:
* Create a new Vivado project targeting the "Kria KV260 Vision AI Starter Kit SOM" board.
* Add the files `output/top.v` and `rtl/xilinx_uram.v` as sources.
* Add the file `constraints/top.xdc` as constraints.
* Run synthesis/implementation.

# Notes

Parallel visiting 16x16 blocks of the bruteforce grid, only triangle.
Input becomes bottleneck? Not really no. But we still optimized it anyways!

Give some cycle perf numbers, and area usage. Scaled to max, not enough CARRY8/LUTs to increase CORE_WIDTH.
Takes 1.34 seconds to process entire BRAM p**2/2 / (16*16) / 400e6

Explain language features used (generics, type checks, easy syntax, functions, reg delays, ...), test setup, verilator, easy python integration, compilation setup, tool compatibility.
