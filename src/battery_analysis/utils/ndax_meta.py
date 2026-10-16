"""NDAX 归档内 Step.xml 元数据提取与 sidecar 落盘。

ndax 文件是 ZIP 容器，内嵌 Step.xml（工步配方：脉冲档位、恒流电流、型号等）
与 TestInfo.xml（运行时测试信息）。档位识别以 ndax 为单一事实来源：
转换出 xlsx 时旁路写一份 <name>.ndaxmeta.json sidecar，供分析链路读取；
文件名解析降级为 sidecar 缺失时的兜底（既有行为不变）。
"""

from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

SIDECAR_SUFFIX = ".ndaxmeta.json"
SCHEMA_VERSION = 1

_STEP_TAG = re.compile(r"Step\d+$")


def sidecar_path_for(xlsx_path) -> Path:
    """sidecar 路径：与 xlsx 同目录同主名，后缀 .ndaxmeta.json。"""
    return Path(xlsx_path).with_suffix(SIDECAR_SUFFIX)


def _parse_xml(data: bytes) -> ET.Element | None:
    """解析 XML 字节：优先按声明解析；声明多字节编码（GB2312 等）时 expat 抛
    ValueError，改为显式解码（utf-8 → gb2312）后解析。"""
    try:
        return ET.fromstring(data)
    except (ET.ParseError, ValueError):
        pass
    for encoding in ("utf-8", "gb2312"):
        try:
            return ET.fromstring(data.decode(encoding))
        except (ET.ParseError, UnicodeDecodeError):
            continue
    logger.warning("XML parse failed for %d bytes", len(data))
    return None


def _as_float(text) -> float | None:
    if text is None:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _element_attr(root: ET.Element | None, path: str, name: str) -> str | None:
    if root is None:
        return None
    el = root.find(path)
    return el.get(name) if el is not None else None


def extract_ndax_metadata(ndax_path) -> dict | None:
    """从 ndax ZIP 提取 Step.xml/TestInfo.xml 权威元数据。

    Returns:
        dict（schema_version/pulse_currents/cc_current/spec_type/remark/
        rate_type/profile_date/test_id/sn/step_name/start_time）；
        ndax 不可读或缺 Step.xml 时返回 None。
    """
    ndax_path = Path(ndax_path)
    try:
        with zipfile.ZipFile(ndax_path) as zf:
            names = set(zf.namelist())
            step_root = (
                _parse_xml(zf.read("Step.xml")) if "Step.xml" in names else None
            )
            info_root = (
                _parse_xml(zf.read("TestInfo.xml"))
                if "TestInfo.xml" in names
                else None
            )
    except (OSError, zipfile.BadZipFile) as exc:
        logger.warning("Cannot read metadata from %s: %s", ndax_path, exc)
        return None
    if step_root is None:
        logger.warning("No parseable Step.xml inside %s", ndax_path.name)
        return None

    # 脉冲档位：所有 PulseData 下的非零 PulseN.Value（负值=放电，取绝对值；0=休息段跳过）
    pulse_currents: list[float] = []
    for pulse_data in step_root.iter("PulseData"):
        for child in pulse_data:
            value = _as_float(child.get("Value"))
            if value:
                pulse_currents.append(abs(value))
    pulse_currents = list(dict.fromkeys(pulse_currents))  # 去重、保序

    # CC 恒流电流：优先放电工步（Step_Type="2"，与 STATUS_MAP 的 CC_DChg 对应），
    # 其余工步的 Limit Curr 作兕底（充放电多工步场景取首个放电值）
    discharge_cc: float | None = None
    fallback_cc: list[float] = []
    for el in step_root.iter():
        if _STEP_TAG.match(el.tag or ""):
            value = _as_float(_element_attr(el, "./Limit/Main/Curr", "Value"))
            if value is None:
                continue
            if el.get("Step_Type") == "2" and discharge_cc is None:
                discharge_cc = value
            else:
                fallback_cc.append(value)
    cc_current = discharge_cc if discharge_cc is not None else (fallback_cc[0] if fallback_cc else None)

    head = step_root.find(".//Head_Info")
    head_value = (
        lambda name: (head.find(name).get("Value") if head is not None and head.find(name) is not None else None)
    )
    info = info_root.find(".//TestInfo") if info_root is not None else None
    info_value = (lambda name: (info.get(name) if info is not None else None))

    return {
        "schema_version": SCHEMA_VERSION,
        "source": "ndax/Step.xml",
        "ndax_file": ndax_path.name,
        "pulse_currents": pulse_currents,
        "cc_current": cc_current,
        "spec_type": head_value("PN"),
        "remark": head_value("Remark"),
        "rate_type": head_value("RateType"),
        "profile_date": step_root.find(".//config").get("date")
        if step_root.find(".//config") is not None
        else None,
        "test_id": info_value("TestID"),
        "sn": info_value("SN"),
        "step_name": info_value("StepName"),
        "start_time": info_value("StartTime"),
    }


def write_sidecar(xlsx_path, metadata: dict) -> Path | None:
    """把元数据写到 xlsx 旁的 sidecar；失败返回 None（增值信息，不抛异常）。"""
    path = sidecar_path_for(xlsx_path)
    try:
        path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path
    except OSError as exc:
        logger.warning("Cannot write sidecar %s: %s", path, exc)
        return None


def read_sidecar(xlsx_path) -> dict | None:
    """读取 xlsx 旁的 sidecar；不存在/损坏返回 None。"""
    path = sidecar_path_for(xlsx_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def ensure_sidecar(ndax_path, xlsx_path) -> dict | None:
    """已有 sidecar 直接返回；否则从 ndax 提取并补写（为旧转换产物回填）。"""
    existing = read_sidecar(xlsx_path)
    if existing is not None:
        return existing
    metadata = extract_ndax_metadata(ndax_path)
    if metadata is not None:
        write_sidecar(xlsx_path, metadata)
    return metadata


def observed_pulse_currents(currents, declared_levels) -> list[float]:
    """实测出现的脉冲档位（转换时计算，供裁决④ 完成性判定）。

    对每个声明档位，数据中存在 |电流采样| 在容差 max(1%, 0.5mA) 内的
    样本即认为该档位已执行；按声明顺序返回子集。声明为空或无有效
    样本返回 []。
    """
    declared = [float(x) for x in (declared_levels or [])]
    if not declared:
        return []
    samples: list[float] = []
    for value in currents:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number == number:  # NaN 跳过
            samples.append(abs(number))
    if not samples:
        return []
    observed: list[float] = []
    for level in declared:
        tolerance = max(abs(level) * 0.01, 0.5)
        if any(abs(sample - level) <= tolerance for sample in samples):
            observed.append(level)
    return observed


def observed_pulse_medians(
    currents, declared_levels, select_ratio: float = 0.05
) -> dict[str, float]:
    """每档实测电流中位数（裁决② 实测层漂移判定的输入）。

    选择窗 ±select_ratio（仓内惯例 ±5%，与 pulse_matcher 对齐）——
    窗宽于告警阈值 max(1%, 0.5mA)，恒定偏差超阈值才能被黄警捕获。
    返回 {档位(str): 中位数}；无样本档位不出现。
    """
    declared = [float(x) for x in (declared_levels or [])]
    if not declared:
        return {}
    samples: list[float] = []
    for value in currents:
        try:
            number = abs(float(value))
        except (TypeError, ValueError):
            continue
        if number == number:  # NaN 跳过
            samples.append(number)
    medians: dict[str, float] = {}
    for level in declared:
        if level <= 0:
            continue
        window = abs(level) * select_ratio
        selected = sorted(s for s in samples if abs(s - level) <= window)
        if not selected:
            continue
        mid = len(selected) // 2
        if len(selected) % 2:
            median = selected[mid]
        else:
            median = (selected[mid - 1] + selected[mid]) / 2.0
        medians[str(level)] = round(median, 6)
    return medians
