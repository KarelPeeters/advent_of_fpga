# Advent of FPGA

https://blog.janestreet.com/advent-of-fpga-challenge-2025/

Implementation of D09P1 (and hopefully P2 eventually).

Targeting _Zynq UltraScale+ Kria KV260_.
https://github.com/tomverbeure/kv260_bringup

# Requirements

[//]: # (TODO pin versions as submodules? and provide exact eg. venv setup instructions)

* Verilator: https://www.veripool.org/verilator/
* HwLang: https://github.com/KarelPeeters/HwLang

# Build and test instructions

```
uv venv
uv pip install -r requirements.txt
uv run maturin develop --manifest-path external/hwlang/rust/hwl_python/Cargo.toml
```

# Vivado synthesis instructions

[//]: # (TODO include synthesis results)