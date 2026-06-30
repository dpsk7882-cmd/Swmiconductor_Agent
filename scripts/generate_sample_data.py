"""Generate sample process data and equipment logs for development/demo."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    np.random.seed(42)
    n = 120
    dates = pd.date_range("2025-01-01", periods=n, freq="D")

    yield_base = 94.0 - np.linspace(0, 4, n) + np.random.normal(0, 0.3, n)
    df = pd.DataFrame(
        {
            "date": dates,
            "lot_id": [f"L{i:04d}" for i in range(n)],
            "chamber_temp_c": 385 + np.random.normal(0, 8, n) + np.linspace(0, 25, n),
            "chamber_pressure_mtorr": 45 + np.random.normal(0, 3, n),
            "rf_power_w": 800 + np.random.normal(0, 40, n) + np.linspace(0, 120, n),
            "gas_flow_sccm": 200 + np.random.normal(0, 10, n),
            "etch_rate_nm_min": 120 + np.random.normal(0, 5, n),
            "overlay_nm": 3.5 + np.random.normal(0, 0.4, n) + np.linspace(0, 2, n),
            "defect_density_cm2": 0.3 + np.random.normal(0, 0.05, n) + np.linspace(0, 1.2, n),
            "particle_count": 50 + np.random.normal(0, 5, n) + np.linspace(0, 30, n),
            "arc_count": 2 + np.random.poisson(0.5, n) + (np.linspace(0, 8, n).astype(int)),
            "yield_pct": yield_base,
        }
    )

    # Inject anomalies in recent lots
    df.loc[df.index[-10:], "chamber_temp_c"] += 45
    df.loc[df.index[-5:], "yield_pct"] -= 3

    df.to_excel(DATA_DIR / "sample_process_data.xlsx", index=False)
    df.to_csv(DATA_DIR / "sample_process_data.csv", index=False)

    logs = []
    for i in range(50):
        if i % 12 == 0:
            logs.append(
                f"2025-02-{i % 28 + 1:02d} 08:00:00 ALARM RF_REFLECTED_POWER_HIGH chamber=ETCH-03"
            )
        elif i % 17 == 0:
            logs.append(
                f"2025-02-{i % 28 + 1:02d} 14:30:00 WARNING pressure_deviation chamber=ETCH-03"
            )
        else:
            logs.append(f"2025-02-{i % 28 + 1:02d} 10:00:00 INFO process_complete lot=L{i:04d}")

    (DATA_DIR / "sample_equipment_log.txt").write_text("\n".join(logs), encoding="utf-8")
    print(f"Sample data written to {DATA_DIR}")


if __name__ == "__main__":
    main()
