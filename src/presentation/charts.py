from __future__ import annotations
from pathlib import Path
from typing import Iterable
import matplotlib
import matplotlib.pyplot as plt

from ..config import FIG_SIZE

matplotlib.rcParams.update({"font.size": 10})


def plot_trend(rows: Iterable[dict], *, x_field: str, y_field: str, title: str,
               out_path: Path | str) -> Path:
    dates = [r[x_field] for r in rows if r.get(x_field) is not None]
    ys = [r[y_field] for r in rows if r.get(y_field) is not None]
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=FIG_SIZE)
    plt.plot(dates, ys, color='teal', linewidth=2)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(y_field.replace('_', ' ').title())
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out
