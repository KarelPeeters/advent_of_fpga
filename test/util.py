from pathlib import Path
import hwl


def compile_manifest() -> hwl.Compile:
    manifest = Path(__file__).parent / "../rtl/hwl.toml"
    source = hwl.Source.new_from_manifest_path(str(manifest))
    return source.compile()
