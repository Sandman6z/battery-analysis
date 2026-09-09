"""NDAX to XLSX conversion engine.

Converts Neware BTS .ndax binary data files to .xlsx format.
No GUI dependencies — pure data processing module.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import NewareNDA as nda
import numpy as np
import pandas as pd
import xlsxwriter

# Status mapping from NewareNDA to Chinese display names
STATUS_MAP: dict[str, str] = {
    "Rest": "搁置",
    "CC_DChg": "恒流放电",
    "Pulse": "脉冲",
}

RECORD_HEADERS = ["循环序号", "工步类型", "电流(A)", "电压(V)", "容量(mAh)"]
STEP_HEADERS = ["循环序号", "工步类型", "容量(mAh)"]
CYCLE_HEADERS = ["循环序号", "起始绝对时间(hh:mm:ss)", "结束绝对时间(hh:mm:ss)", "放电容量(mAh)"]


def _ts_str(ts: Any) -> str:
    """Format a timestamp without microseconds and timezone offset.

    Args:
        ts: Timestamp object (pandas Timestamp or similar).

    Returns:
        Formatted string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    s = str(ts)
    # Chop microseconds and timezone
    idx = s.find(".")
    if idx != -1:
        s = s[:idx]
    # Remove +08:00 type timezone suffix
    if "+" in s:
        s = s[: s.rfind("+")]
    elif "-" in s[10:]:  # only look after date portion for TZ
        s = s[: s.rfind("-")]
    return s


def _get_ndax_files(input_dir: Path) -> list[Path]:
    """Get all .ndax files in a directory, sorted by name."""
    return sorted(input_dir.glob("*.ndax"))


def _build_record_sheet(wb: xlsxwriter.Workbook, df: pd.DataFrame, filename: str) -> None:
    """Build the Record sheet with all individual data points."""
    ws = wb.add_worksheet(name="Record")
    ws.write_row(0, 0, [filename])
    ws.write_row(1, 0, RECORD_HEADERS)

    cycles = df["Cycle"].values
    steps = df["Status"].map(STATUS_MAP).values
    currents = (df["Current(mA)"].values / 1000.0).round(9)
    voltages = df["Voltage"].values.round(4)

    statuses = df["Status"].values
    chg = df["Charge_Capacity(mAh)"].values
    dchg = df["Discharge_Capacity(mAh)"].values
    capacities = np.where(
        statuses == "CC_DChg", dchg,
        np.where(statuses == "Pulse", chg - dchg, 0.0)
    ).round(6)

    for i, row_data in enumerate(zip(cycles, steps, currents, voltages, capacities), start=2):
        ws.write_row(i, 0, row_data)


def _build_step_sheet(wb: xlsxwriter.Workbook, df: pd.DataFrame, filename: str) -> None:
    """Build the Step sheet with aggregated data per cycle+step."""
    ws = wb.add_worksheet(name="Step")
    ws.write_row(0, 0, [filename])
    ws.write_row(1, 0, STEP_HEADERS)

    row = 2
    for (cycle, _step, status), grp in df.groupby(["Cycle", "Step", "Status"], sort=False):
        first = grp.iloc[0]
        last = grp.iloc[-1]
        dchg_delta = last["Discharge_Capacity(mAh)"] - first["Discharge_Capacity(mAh)"]

        if status == "CC_DChg":
            cap = dchg_delta
        else:
            chg_delta = last["Charge_Capacity(mAh)"] - first["Charge_Capacity(mAh)"]
            cap = chg_delta - dchg_delta

        ws.write_row(row, 0, [cycle, STATUS_MAP[status], round(float(cap), 3)])
        row += 1


def _build_cycle_sheet(wb: xlsxwriter.Workbook, df: pd.DataFrame, filename: str) -> None:
    """Build the Cycle sheet with aggregated data per cycle."""
    ws = wb.add_worksheet(name="Cycle")
    ws.write_row(0, 0, [filename])
    ws.write_row(1, 0, CYCLE_HEADERS)

    row = 2
    for cycle, grp in df.groupby("Cycle", sort=True):
        total_dchg = 0.0
        for _, step_grp in grp.groupby("Step", sort=True):
            total_dchg += (
                step_grp["Discharge_Capacity(mAh)"].iloc[-1]
                - step_grp["Discharge_Capacity(mAh)"].iloc[0]
            )
        ws.write_row(row, 0, [
            cycle,
            _ts_str(grp["Timestamp"].iloc[0]),
            _ts_str(grp["Timestamp"].iloc[-1]),
            round(total_dchg, 3),
        ])
        row += 1


def convert_one(ndax_path: str | Path, xlsx_path: str | Path | None = None) -> str:
    """Convert a single .ndax file to .xlsx.

    Args:
        ndax_path: Path to the .ndax file.
        xlsx_path: Output path. If None, derived by replacing extension
                   and placing in ../2_xlsx/ directory.

    Returns:
        Path to the generated .xlsx file.

    Raises:
        FileNotFoundError: ndax_path does not exist.
        ValueError: File parsing failed.
    """
    ndax_path = Path(ndax_path)
    if not ndax_path.exists():
        raise FileNotFoundError(f"NDAX file not found: {ndax_path}")

    if xlsx_path is None:
        out_dir = ndax_path.parent.parent / "2_xlsx"
        out_dir.mkdir(parents=True, exist_ok=True)
        xlsx_path = out_dir / f"{ndax_path.stem}.xlsx"
    else:
        xlsx_path = Path(xlsx_path)
        xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = nda.read(str(ndax_path), software_cycle_number=False)
    except Exception as e:
        raise ValueError(f"Failed to parse {ndax_path}: {e}") from e

    filename = ndax_path.name
    wb = xlsxwriter.Workbook(str(xlsx_path))

    _build_cycle_sheet(wb, df, filename)
    _build_step_sheet(wb, df, filename)
    _build_record_sheet(wb, df, filename)

    wb.close()
    return str(xlsx_path)


def convert_batch(input_dir: str | Path, max_workers: int | None = None) -> dict:
    """Convert all .ndax files in a directory using parallel processes.

    Args:
        input_dir: Directory containing .ndax files.
        max_workers: Number of parallel worker processes. Defaults to CPU count.

    Returns:
        {'success': [file...], 'skipped': [file...], 'failed': [(file, error)...]}
    """
    input_dir = Path(input_dir)
    ndax_files = _get_ndax_files(input_dir)
    out_dir = input_dir.parent / "2_xlsx"
    out_dir.mkdir(parents=True, exist_ok=True)

    result: dict = {"success": [], "skipped": [], "failed": []}

    pending = []
    for ndax_path in ndax_files:
        xlsx_path = out_dir / f"{ndax_path.stem}.xlsx"
        if xlsx_path.exists():
            result["skipped"].append(ndax_path.name)
        else:
            pending.append((ndax_path, xlsx_path))

    if not pending:
        return result

    max_workers = max_workers or os.cpu_count()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        fut_map = {
            executor.submit(convert_one, ndax_path, xlsx_path): ndax_path
            for ndax_path, xlsx_path in pending
        }
        for future in as_completed(fut_map):
            ndax_path = fut_map[future]
            try:
                future.result()
                result["success"].append(ndax_path.name)
            except Exception as e:
                result["failed"].append((ndax_path.name, str(e)))

    return result


def get_ndax_files(directory: str | Path) -> list[str]:
    """Get all .ndax file names in a directory (non-recursive)."""
    return [p.name for p in _get_ndax_files(Path(directory))]
