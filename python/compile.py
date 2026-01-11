from pathlib import Path
import hwl
from util import compile_manifest


def main() -> None:
    c = compile_manifest()
    top: hwl.Module = c.resolve("top.top")

    out_dir = Path(__file__).parent / "../output"
    out_dir.mkdir(exist_ok=True, parents=True)

    out_file = out_dir / "output.v"
    out_file.write_text(top.as_verilog().source)

    print(f"Compiled successfully and wrote to {out_file}")


if __name__ == "__main__":
    main()
