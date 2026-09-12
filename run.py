import sys
from pathlib import Path

from pipeline import run_pipeline


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python run.py images\\product1.jpg")
        raise SystemExit(2)

    image = Path(sys.argv[1])
    run_pipeline(image)


if __name__ == "__main__":
    main()
