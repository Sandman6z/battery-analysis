"""ndax sidecar 模块（utils/ndax_meta.py）单测：Step.xml 提取、落盘、回填。"""

import json
import zipfile

from battery_analysis.utils.ndax_meta import (
    SCHEMA_VERSION,
    SIDECAR_SUFFIX,
    ensure_sidecar,
    extract_ndax_metadata,
    observed_pulse_currents,
    read_sidecar,
    sidecar_path_for,
    write_sidecar,
)

# 真实 CR2450 样本（BatteryR/BattData_ndax）的字段结构等价缩小版
STEP_XML = b"""<?xml version="1.0" encoding="GB2312"?>
<root>
  <config type="Step File" version="17" client_version="BTSDA BTS Client" date="20250610100145">
    <Head_Info>
      <Operate Value="66"/>
      <PN Value="CR2450"/>
      <Remark Value="CR2450-1S1P, DC 2517, QA Test (30-26-15-6mA, CC 10mAh 1mA)"/>
      <RateType Value="103"/>
    </Head_Info>
    <Step_Info Num="3">
      <Step1 Step_ID="1" Step_Type="4">
        <Record><Main><Time Value="10000"/></Main></Record>
        <Limit><Main><Time Value="1800000"/></Main></Limit>
      </Step1>
      <Step2 Step_ID="2" Step_Type="2">
        <Record><Main><Time Value="10000"/></Main></Record>
        <Limit><Main><Curr Value="1"/><Cap Value="36000"/><Stop_Volt Value="9500"/></Main></Limit>
      </Step2>
      <Step4 Step_ID="4" Step_Type="16">
        <PulseData Pulse_Mode="1" Pulse_VolHi="40000" Pulse_VolLo="10000" Cycle_Count="10" Count="8">
          <Pulse1 Value="0" Time="59000"/>
          <Pulse2 Value="-30" Time="1000"/>
          <Pulse3 Value="0" Time="59000"/>
          <Pulse4 Value="-26" Time="1000"/>
          <Pulse5 Value="0" Time="58000"/>
          <Pulse6 Value="-15" Time="2000"/>
          <Pulse7 Value="0" Time="55000"/>
          <Pulse8 Value="-6" Time="5000"/>
        </PulseData>
      </Step4>
    </Step_Info>
  </config>
</root>
"""

TESTINFO_XML = b"""<?xml version="1.0" encoding="GB2312"?>
<root>
  <config type="Test Info File" version="1" date="20250707184610">
    <TestInfo TestID="2818580619" SN="CR2450"
              StepName="CR2450-1S1P_QATest_30-26-15-6mA_CC-1mA-10mAh - ATMT.xml"
              StartTime="2025-06-10 10:01:49"/>
  </config>
</root>
"""


def _make_ndax(path, step_xml=STEP_XML, testinfo_xml=TESTINFO_XML):
    with zipfile.ZipFile(path, "w") as zf:
        if step_xml is not None:
            zf.writestr("Step.xml", step_xml)
        if testinfo_xml is not None:
            zf.writestr("TestInfo.xml", testinfo_xml)
        zf.writestr("data.ndc", b"\x00fake")
    return path


class TestExtractNdaxMetadata:
    def test_pulse_levels_from_discharge_pulses(self, tmp_path):
        """非零 PulseN.Value 取 abs 去重保序 → [30, 26, 15, 6]（0=休息段跳过）"""
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax"))
        assert meta is not None
        assert meta["pulse_currents"] == [30.0, 26.0, 15.0, 6.0]

    def test_cc_current_prefers_discharge_step(self, tmp_path):
        """Step_Type=2（放电）的 Limit/Main/Curr 优先于其他工步"""
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax"))
        assert meta["cc_current"] == 1.0

    def test_cc_current_falls_back_to_any_step(self, tmp_path):
        """无放电工步时退到首个非空 Limit Curr"""
        step_xml = STEP_XML.replace(b'Step_Type="2"', b'Step_Type="1"')
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax", step_xml=step_xml))
        assert meta["cc_current"] == 1.0

    def test_head_and_testinfo_fields(self, tmp_path):
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax"))
        assert meta["schema_version"] == SCHEMA_VERSION
        assert meta["source"] == "ndax/Step.xml"
        assert meta["spec_type"] == "CR2450"
        assert meta["rate_type"] == "103"
        assert "QA Test" in meta["remark"]
        assert meta["profile_date"] == "20250610100145"
        assert meta["test_id"] == "2818580619"
        assert meta["sn"] == "CR2450"
        assert meta["start_time"] == "2025-06-10 10:01:49"
        assert meta["step_name"].endswith("ATMT.xml")

    def test_missing_step_xml_returns_none(self, tmp_path):
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax", step_xml=None))
        assert meta is None

    def test_not_a_zip_returns_none(self, tmp_path):
        bad = tmp_path / "bad.ndax"
        bad.write_bytes(b"definitely not a zip archive")
        assert extract_ndax_metadata(bad) is None

    def test_missing_file_returns_none(self, tmp_path):
        assert extract_ndax_metadata(tmp_path / "nope.ndax") is None

    def test_step_without_pulses_gives_empty_list(self, tmp_path):
        """有 Step.xml 但无 PulseData → 空列表（消费端回落文件名解析），不是 None"""
        step_xml = STEP_XML.replace(b"<PulseData", b"<NoPulse").replace(b"PulseData>", b"NoPulse>")
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax", step_xml=step_xml))
        assert meta is not None
        assert meta["pulse_currents"] == []


class TestSidecarIO:
    def test_sidecar_path_for(self):
        assert sidecar_path_for("C:/a/b/BTS83_1.xlsx").name == "BTS83_1" + SIDECAR_SUFFIX

    def test_write_read_roundtrip(self, tmp_path):
        xlsx = tmp_path / "BTS83_40_9_1.xlsx"
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax"))
        path = write_sidecar(xlsx, meta)
        assert path is not None and path.exists()
        assert read_sidecar(xlsx) == meta

    def test_read_missing_returns_none(self, tmp_path):
        assert read_sidecar(tmp_path / "absent.xlsx") is None

    def test_read_corrupt_returns_none(self, tmp_path):
        xlsx = tmp_path / "bad.xlsx"
        xlsx.with_suffix(SIDECAR_SUFFIX).write_text("{not json", encoding="utf-8")
        assert read_sidecar(xlsx) is None

    def test_write_failure_returns_none_not_raise(self, tmp_path):
        meta = extract_ndax_metadata(_make_ndax(tmp_path / "t.ndax"))
        # sidecar 目标路径已存在为目录 → OSError 被吞掉返回 None
        target = tmp_path / "blocked.xlsx"
        sidecar_path_for(target).mkdir(parents=True)
        assert write_sidecar(target, meta) is None


class TestEnsureSidecar:
    def test_backfill_creates_sidecar(self, tmp_path):
        ndax = _make_ndax(tmp_path / "t.ndax")
        xlsx = tmp_path / "t.xlsx"
        xlsx.write_bytes(b"")  # 旧转换产物：有 xlsx 无 sidecar
        meta = ensure_sidecar(ndax, xlsx)
        assert meta is not None
        assert sidecar_path_for(xlsx).exists()

    def test_existing_sidecar_reused_without_ndax(self, tmp_path):
        ndax = tmp_path / "t.ndax"
        ndax.write_bytes(b"broken zip - must not be opened")
        xlsx = tmp_path / "t.xlsx"
        xlsx.write_bytes(b"")
        expected = {"pulse_currents": [30, 26, 15, 6]}
        xlsx.with_suffix(SIDECAR_SUFFIX).write_text(
            json.dumps(expected), encoding="utf-8"
        )
        assert ensure_sidecar(ndax, xlsx) == expected

    def test_broken_ndax_returns_none_and_skips_write(self, tmp_path):
        ndax = tmp_path / "t.ndax"
        ndax.write_bytes(b"not a zip")
        xlsx = tmp_path / "t.xlsx"
        xlsx.write_bytes(b"")
        assert ensure_sidecar(ndax, xlsx) is None
        assert not sidecar_path_for(xlsx).exists()


class TestObservedPulseCurrents:
    """转换时实测算档（裁决④ 完成性证据）。"""

    def test_all_declared_levels_observed(self):
        samples = [-30.0, -26.1, -15.0, -6.0, 0.0]
        assert observed_pulse_currents(samples, [30, 26, 15, 6]) == [30.0, 26.0, 15.0, 6.0]

    def test_missing_level_excluded_preserves_declared_order(self):
        # 26 档未执行（CF224642T 事故场景：声明 4 实测 3）
        samples = [-60.0, -30.0, -15.0, -6.0]
        assert observed_pulse_currents(samples, [30, 26, 15, 6]) == [30.0, 15.0, 6.0]

    def test_within_one_percent_tolerance(self):
        assert observed_pulse_currents([-30.2], [30]) == [30.0]

    def test_nan_and_invalid_skipped(self):
        import math

        samples = [float("nan"), None, "junk", -15.0]
        assert observed_pulse_currents(samples, [15, 6]) == [15.0]

    def test_empty_declared_returns_empty(self):
        assert observed_pulse_currents([-30.0], []) == []
        assert observed_pulse_currents([-30.0], None) == []

    def test_no_valid_samples_returns_empty(self):
        assert observed_pulse_currents([], [30]) == []
        assert observed_pulse_currents([float("nan")], [30]) == []
