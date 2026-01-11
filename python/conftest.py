import os
import subprocess

# Tell verilator to use ccache if installed
try:
    subprocess.check_output(["ccache", "--version"])
except FileNotFoundError:
    pass
else:
    os.environ["OBJCACHE"] = "ccache"
