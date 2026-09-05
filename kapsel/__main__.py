"""
Kapsel execution module entry point: allows running `python -m kapsel`.
"""
import sys
from kapsel.cli import main

if __name__ == "__main__":
    sys.exit(main())
