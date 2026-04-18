from __future__ import annotations

import argparse
import sys
from pathlib import Path


def load_trace(path: Path):
    """Load trace CSV; return DataFrame with columns cycle, miss_rate, mpki."""
    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError(
            "pandas is required. Install with e.g. `pip install pandas`"
        ) from None

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    required = ("cycle", "miss_rate", "mpki")
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV missing column(s) {missing}; found {list(df.columns)}"
        )

    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=list(required))
    if df.empty:
        raise ValueError("No numeric rows parsed from CSV")

    df = df[list(required)].sort_values("cycle", kind="mergesort").reset_index(drop=True)
    return df


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot L1D sliding-window miss_rate and MPKI vs cycle from trace CSV."
    )
    ap.add_argument(
        "csv",
        type=Path,
        help="Path to trace CSV (e.g. l1d_window_trace.csv)",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Figure output path (.png, .pdf, .svg). Default: <csv_stem>_plot.png next to CSV",
    )
    ap.add_argument(
        "--show",
        action="store_true",
        help="Open an interactive matplotlib window",
    )
    ap.add_argument("--dpi", type=int, default=150, help="Raster DPI when saving PNG (default 150)")
    ap.add_argument(
        "--x-window",
        type=int,
        default=None,
        metavar="N",
        help="Maximum simulation-cycle span on the x-axis (zoom). "
        "If the trace spans more than N cycles, the plot is limited to a window "
        "of width N; use --x-window-anchor to choose start vs end. Omit for full range.",
    )
    ap.add_argument(
        "--x-window-anchor",
        choices=("start", "end"),
        default="end",
        help="With --x-window: align the visible window to the first N cycles (start) "
        "or the last N cycles (end). Default: end",
    )
    args = ap.parse_args()

    if not args.csv.is_file():
        print(f"error: not a file: {args.csv}", file=sys.stderr)
        return 1

    try:
        df = load_trace(args.csv)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "error: matplotlib is required. Install with e.g. `pip install matplotlib`",
            file=sys.stderr,
        )
        return 1

    out = args.output
    if out is None:
        out = args.csv.with_name(args.csv.stem + "_plot.png")

    fig, (ax0, ax1) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(10, 6),
        constrained_layout=True,
    )
    ax0.plot(df["cycle"], df["miss_rate"], color="C0", linewidth=0.8)
    ax0.set_ylabel("miss rate")
    ax0.set_title("L1D sliding-window miss rate and MPKI vs cycle")
    ax0.grid(True, alpha=0.3)

    ax1.plot(df["cycle"], df["mpki"], color="C1", linewidth=0.8)
    ax1.set_xlabel("cycle")
    ax1.set_ylabel("MPKI")
    ax1.grid(True, alpha=0.3)

    if args.x_window is not None:
        if args.x_window <= 0:
            print("error: --x-window must be a positive integer", file=sys.stderr)
            return 1
        c0 = float(df["cycle"].min())
        c1 = float(df["cycle"].max())
        span = c1 - c0
        if span > float(args.x_window):
            if args.x_window_anchor == "end":
                x_min, x_max = c1 - float(args.x_window), c1
            else:
                x_min, x_max = c0, c0 + float(args.x_window)
            ax1.set_xlim(x_min, x_max)

    fig.savefig(out, dpi=args.dpi)
    print(f"wrote {out.resolve()}")

    if args.show:
        plt.show()
    else:
        plt.close(fig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
