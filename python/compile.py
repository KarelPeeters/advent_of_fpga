from pathlib import Path
import hwl
from util import compile_manifest


def main() -> None:
    MAX_POINT_COUNT = 2 * (1024 * 4) * 64
    COORD_LIMIT = 10**5
    RAM_PIPELINE = 8
    CORE_WIDTH = 16

    c = compile_manifest()
    top: hwl.Module = c.resolve("top.top_generic")(
        MAX_POINT_COUNT=MAX_POINT_COUNT,
        COORD_LIMIT=COORD_LIMIT,
        RAM_PIPELINE=RAM_PIPELINE,
        CORE_WIDTH=CORE_WIDTH,
    )

    out_dir = Path(__file__).parent / "../output"
    out_dir.mkdir(exist_ok=True, parents=True)

    out_file = out_dir / "output.v"
    out_file.write_text(top.as_verilog().source)

    print(f"Compiled successfully and wrote to {out_file}")


if __name__ == "__main__":
    main()
