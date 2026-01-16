# Advent of FPGA

My submission to [Jane Street's Advent of FPGA Challenge 2025](https://blog.janestreet.com/advent-of-fpga-challenge-2025/).

Implements [Advent of code 2025 day 9 part 1](https://adventofcode.com/2025/day/9), targeting the [Zynq UltraScale+ Kria KV260](https://www.amd.com/en/products/system-on-modules/kria/k26/kv260-vision-starter-kit.html)

### HwLang, an experimental RTL language

This project serves as a demo of the experimental RTL language I'm working on, with placeholder name [HwLang](https://github.com/KarelPeeters/HwLang).

The goal is to bring some of the major improvements that have happened in the software world in language design and tooling quality to the hardware world. It's also a chance to solve the major flaws in SystemVerilog and VHDL, with features like stronger compile-time type checking, more powerful generics, higher-order functions, and better abstractions through structs/enums/interfaces. The compiler lowers everything into simple Verilog, which should be compatible with all backend tools used in typical FPGA or ASIC projects. The compiler library also serves as the base for an LSP server, and a python package which can be used to drive compilation and for design verification.

The [README](https://github.com/KarelPeeters/HwLang/blob/main/README.md) of the HwLang project contains more detail on the goals and features of the language.

### The design itself

For Advent of code D09P1, we get a list of points and need to compute the maximum area between any two  points in the list. There's probably some clever O(n*log(n)) algorithm using a quadtree to accomplish this, but in hardware we can also get away with just bruteforcing the solution and still get reasonable performance.

For IO we'll match the original challenge exactly:
* The input is a stream of ascii characters containing newline and comma separated decimal strings.
* The output is again a stream of ascii characters, the final area as a decimal string, followed by a newline.

![Top module diagram](./doc/FPGA%20top.drawio.svg)

The input/output conversions are handled in separate modules. The core modules to receives a stream of points and emits the result as a single integer.

#### Core

![Core module diagram](./doc/FPGA%20core.drawio.svg)

The core consists of a large URAM block, two state machines and a pipelined datapath array and reduction tree.

The datapath consists of a 2D array of area calculations, followed by a max-reduction tree. The 2D array allows us to feed in two sets of `CORE_WIDTH` points, and get the maximum area between any possible pair of `CORE_WIDTH * CORE_WIDTH` points. This is then followed by a max-reduction tree which at each stage takes the maximum value of pairs of areas, until only a single max area remains at the output. As an additional input it takes in valid masks, which are used to mask values to ensure correct results when we can't fill up the entire core. Vivado is nice enough to automatically map the area multiplications to DSP slices. This combined with heavy pipelining to allows it to run at 400MHz.

The URAM, full name [Xilinx UltraRAM](https://docs.amd.com/r/en-US/ug1273-versal-acap-design/UltraRAM-Primitives) is a dual-port memory primitive available on Xilinx FPGAs. The KV260 has 64 URAM blocks, we'll use all of them. The port width is set to match `CORE_WIDTH`. Each clock cycle we read two different lines from memory using the two ports, and send each line to one of the inputs of the 2D array. Because lots of URAM blocks get chained together to form a large single RAM, this again needs lots of pipeline registers.

The _front_ state machine receives input points, batches them until they fill a URAM row, and writes them to the next URAM address. Once it received the signal that the input is done, it tells the _back_ state machine to start the computation. It then waits until the computation is done, and emits the output value.

The _back_ state machine walks over the grid, sending read indices to the memory and valid masks to the 2D array. We don't visit the entire N*N grid of possible pairs, we only visit the lower triangle to skip duplicate work. When done, we wait for the data pipeline to clear and send the result back to the _front_ state machine.

#### Source files

All rtl source files are contained in the `rtl` folder.
* `top.kh` and `core.kh` contain the top and core modules respectively. The actual top parameters are filled in in `python/compile.py`.
* `common.kh` provides common definition used throughout the different modules.
* `string.kh` contains the to/from string conversion modules.
* `xilinx_uram.v` and `xilinx_uram.kh` contain the right verilog for URAM inference and the wrapper around it.
* `transpose.kh` and `div.kh` are a transpose module and a division optimization utility, not used in the final design.

### Synthesis results

The parametrization of the final design is:
* `MAX_POINT_COUNT = 2 * (1024 * 4) * 64`: We store up to 524288 points in memory, using the full URAM capacity of the target device.
* `COORD_LIMIT = 10**5`: Point coordinates can have up to 5 decimal digits, which takes 17 bits to store.
* `CORE_WIDTH = 16`: The 2D core is 16x16, calculating 256 areas per cycle.

The design synthesizes successfully at 400MHz, with the following utilization:

```
Name                        CLB LUTs    CLB Registers   CARRY8   URAM    DSPs
top_generic                 36103       47976           4464     64      256
instance_8 (int_to_chars)   222         161             9        0       0
instance_5 (core)           35801       47702           4447     64      256
instance_2 (parse_points)   113         113             8        0       0
```

If we fill up the entire memory with points, the calculation takes
`(524288**2) / 2 / (16*16)` cycles, 1.34 seconds. The quadratic cost of the bruteforce calculation dominates the time needed for IO.

### Verification

Verification for design written in HwLang is very convenient: elaboration, instantiation modules and driving ports is all possible from python, with no other setup. This allows us to write very idiomatic pytest tests, using a combination of manual inputs and randomization. All tests are located in the `python` folder. `util.py` has some utilities, most notably a generic test that sends arbitrary axi input data and collects arbitrary axi output data, used by many other tests.
The `test_div` tests use another cool feature of the python package: functions defined in the RTL language can be called directly from python, without having to write a wrapper module.

### Setup, build, test, synthesis instructions

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
