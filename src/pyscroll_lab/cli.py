"""Command line entry point: `lab info`, `lab serve`."""

import argparse
import sys

from pyscroll_lab import __version__
from pyscroll_lab.config import get_settings


def cmd_info() -> int:
    s = get_settings()
    print(f"pyscroll-lab {__version__}")
    print(f"data_root:      {s.data_root or '(not set: export LAB_DATA_ROOT)'}")
    for name, path in s.data_sources().items():
        print(f"  {name:<10} {'ok     ' if path.exists() else 'MISSING'} {path}")
    print(f"warehouse:      {s.warehouse_path} ({'built' if s.warehouse_path.exists() else 'not built'})")
    return 1 if s.missing_sources() else 0


def cmd_serve(host: str, port: int) -> int:
    import uvicorn

    uvicorn.run("pyscroll_lab.api:app", host=host, port=port, reload=False)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lab")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info", help="show settings and check the raw data paths")
    serve = sub.add_parser("serve", help="run the API locally")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8077)
    args = parser.parse_args(argv)
    if args.cmd == "info":
        return cmd_info()
    return cmd_serve(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
