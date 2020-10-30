import sys
import pkg_resources
from subprocess import Popen, PIPE as SPROC_PIPE, run as sp_run
from functools import partial
from shutil import get_terminal_size
from pprint import PrettyPrinter
from math import floor


PACKAGES = [dist.project_name for dist in pkg_resources.working_set]
CMD_PIP_VERS = [sys.executable, "-m", "pip", "-V"]
CMD_PIP_UPGRADE = [sys.executable, "-m", "pip", "install", "--upgrade"]
HELP_CMD = "'-h', '--help'"
HELP_MSG = """Available commands:
-h, --help
    Print this message.
-l, --list
    Print installed packages.
-v, --versions
    Print pip, python3, versions.
-u, --upgrade
    Upgrade all installed packages.
-uD, --upgrade-debug
    Upgrade all packages with full pip output."""


def _with_progress_bar(func, symbol="■"):
    def _func_with_progress_bar(*args, **kwargs):
        max_width, _ = get_terminal_size()
        gen = func(*args, **kwargs)
        while True:
            try:
                progress = next(gen)

            except StopIteration as e:
                sys.stdout.write("\n")
                return e.value

            else:
                space_to_pct = [3, 2, 1][len(str(round(progress))) - 1]
                msg = f"[%s]{' ' * space_to_pct}{progress}%%"
                bar_width = max_width - len(msg) + 2
                filled = int(round(bar_width / 100 * progress))
                space_left = bar_width - filled
                bar = f"{symbol * filled}{' ' * space_left}"
                sys.stdout.write(f"{msg}\r" % bar)
                sys.stdout.flush()

    return _func_with_progress_bar


with_progress_bar = partial(_with_progress_bar, symbol="■")


@with_progress_bar
def upgrade_all_packages():
    progress_per_package = round(100 / len(PACKAGES), 2)
    cmd = CMD_PIP_UPGRADE + PACKAGES
    i = 0
    with Popen(cmd, stdout=SPROC_PIPE, universal_newlines=True) as p:
        for line in p.stdout:
            if line[:31] == "Requirement already up-to-date:":
                i += 1
                yield floor(i * progress_per_package)

            else:
                print(f"{line}")

    yield 100


def main():
    max_width, _ = get_terminal_size()
    pp = PrettyPrinter(indent=4, width=max_width, compact=True)

    if len(sys.argv) == 1:
        print(f"Arg required, for help: {HELP_CMD}")

    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print(f"{HELP_MSG}")

    elif sys.argv[1] == "-l" or sys.argv[1] == "--list":
        pp.pprint(PACKAGES)

    elif sys.argv[1] == "-v" or sys.argv[1] == "--versions":
        sp_run(CMD_PIP_VERS)
        print(f"Python: {sys.version}")

    elif sys.argv[1] == "-u" or sys.argv[1] == "--upgrade":
        print("Upgrading all packages...")
        upgrade_all_packages()

    elif sys.argv[1] == "-uD" or sys.argv[1] == "--upgrade-debug":
        print("Upgrading all packages with full pip output...")
        sp_run(CMD_PIP_UPGRADE + PACKAGES)

    else:
        print(f"Invalid arg, for help: {HELP_CMD}")


if __name__ == "__main__":
    main()

