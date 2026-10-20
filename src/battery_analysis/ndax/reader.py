"""Read Neware recipe levels and build the legacy analysis views in memory."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import NewareNDA as nda
import numpy as np
import pandas as pd

from battery_analysis.ndax.converter import (
    CYCLE_HEADERS,
    RECORD_HEADERS,
    STATUS_MAP,
    STEP_HEADERS,
    _ts_str,
)


def _xml_root(raw: bytes) -> ET.Element:
    # BTS files use GB2312; ElementTree's byte parser cannot decode it on all Python builds.
    match = re.search(rb'encoding\s*=\s*["\']([^"\']+)', raw[:200])
    encoding = match.group(1).decode("ascii") if match else "utf-8"
    return ET.fromstring(raw.decode(encoding))


def pulse_levels(root: ET.Element) -> list[float]:
    """Recipe PulseData currents (mA), in declared order; no filename inference."""
    levels = []
    for pulse_data in root.findall(".//Step_Info/*/PulseData"):
        children = list(pulse_data)
        if len(children) != int(pulse_data.attrib["Count"]):
            raise ValueError("Step.xml PulseData.Count does not match pulse steps")
        for pulse in children:
            if not re.fullmatch(r"Pulse\d+", pulse.tag):
                raise ValueError(f"Unexpected pulse element: {pulse.tag}")
            current = float(pulse.attrib["Value"])
            if current < 0:
                levels.append(abs(current))
    if not levels or not all(np.isfinite(level) for level in levels):
        raise ValueError("Step.xml has no reliable discharge pulse currents")
    if len(levels) != len(set(levels)):
        raise ValueError("Step.xml has duplicate discharge pulse levels")
    return levels


def recipe_levels(ndax_path: str | Path) -> list[float]:
    try:
        with zipfile.ZipFile(ndax_path) as archive:
            return pulse_levels(_xml_root(archive.read("Step.xml")))
    except (zipfile.BadZipFile, UnicodeError, ET.ParseError) as e:
        raise ValueError(f"Cannot read Step.xml in {ndax_path}: {e}") from e


def profile_levels(profile_path: str | Path) -> list[float]:
    return pulse_levels(_xml_root(Path(profile_path).read_bytes()))


def read_analysis_views(path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """One NDA read, same Cycle/Step/Record rows as the standalone xlsx exporter."""
    path = Path(path)
    df = nda.read(str(path), software_cycle_number=False)
    if df.empty or df["Timestamp"].isna().all():
        raise ValueError(f"No measured Timestamp: {path}")
    filename = path.name
    def headers(labels):
        return pd.DataFrame([[filename] + [None] * (len(labels) - 1), labels])

    statuses = df["Status"].to_numpy()
    capacities = np.where(
        statuses == "CC_DChg", df["Discharge_Capacity(mAh)"].to_numpy(),
        np.where(statuses == "Pulse", df["Charge_Capacity(mAh)"].to_numpy() - df["Discharge_Capacity(mAh)"].to_numpy(), 0.0),
    ).round(6)
    record_rows = pd.DataFrame({
        0: df["Cycle"].to_numpy(),
        1: df["Status"].map(STATUS_MAP).to_numpy(),
        2: (df["Current(mA)"].to_numpy() / 1000.0).round(9),
        3: df["Voltage"].to_numpy().round(4),
        4: capacities,
    })

    steps = []
    for (cycle, _step, status), grp in df.groupby(["Cycle", "Step", "Status"], sort=False, observed=False):
        first, last = grp.iloc[0], grp.iloc[-1]
        discharge = last["Discharge_Capacity(mAh)"] - first["Discharge_Capacity(mAh)"]
        capacity = discharge if status == "CC_DChg" else last["Charge_Capacity(mAh)"] - first["Charge_Capacity(mAh)"] - discharge
        steps.append([cycle, STATUS_MAP.get(status, status), round(float(capacity), 3)])

    cycles = []
    for cycle, grp in df.groupby("Cycle", sort=True):
        total = sum(
            part["Discharge_Capacity(mAh)"].iloc[-1] - part["Discharge_Capacity(mAh)"].iloc[0]
            for _, part in grp.groupby("Step", sort=True)
        )
        cycles.append([cycle, _ts_str(grp["Timestamp"].iloc[0]), _ts_str(grp["Timestamp"].iloc[-1]), round(total, 3)])
    del df
    return (
        pd.concat([headers(CYCLE_HEADERS), pd.DataFrame(cycles)], ignore_index=True),
        pd.concat([headers(STEP_HEADERS), pd.DataFrame(steps)], ignore_index=True),
        pd.concat([headers(RECORD_HEADERS), record_rows], ignore_index=True),
    )
