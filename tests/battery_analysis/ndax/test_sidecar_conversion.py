"""转换链路 sidecar 接线：convert_one 写入、convert_batch/ConvertWorker 跳过分支回填。"""

import zipfile
from pathlib import Path

import pandas as pd

from battery_analysis.ndax import converter as conv
from battery_analysis.utils.ndax_meta import read_sidecar

STEP_XML = b"""<?xml version="1.0" encoding="GB2312"?>
<root>
  <config type="Step File" version="17" date="20250610100145">
    <Head_Info>
      <PN Value="CR2450"/>
      <Remark Value="CR2450-1S1P, DC 2517, QA Test (30-26-15-6mA, CC 10mAh 1mA)"/>
      <RateType Value="103"/>
    </Head_Info>
    <Step_Info Num="3">
      <Step2 Step_ID="2" Step_Type="2">
        <Limit><Main><Curr Value="1"/><Cap Value="36000"/></Main></Limit>
      </Step2>
      <Step4 Step_ID="4" Step_Type="16">
        <PulseData Pulse_Mode="1" Cycle_Count="10" Count="8">
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
  <config type="Test Info File" version="1">
    <TestInfo TestID="2818580619" SN="CR2450" StartTime="2025-06-10 10:01:49"/>
  </config>
</root>
"""


def _make_ndax(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("Step.xml", STEP_XML)
        zf.writestr("TestInfo.xml", TESTINFO_XML)
        zf.writestr("data.ndc", b"\x00fake")
    return path


def _fake_df() -> pd.DataFrame:
    """convert_one 消费的最小 DataFrame（nda.read 打桩返回）。"""
    return pd.DataFrame(
        {
            "Cycle": [1, 1, 1],
            "Step": [2, 4, 4],
            "Status": ["CC_DChg", "Pulse", "Rest"],
            "Current(mA)": [-1.0, -30.0, 0.0],
            "Voltage": [3.0, 2.9, 3.1],
            "Charge_Capacity(mAh)": [0.0, 0.02, 0.0],
            "Discharge_Capacity(mAh)": [1.0, 1.05, 1.05],
            "Timestamp": pd.to_datetime(
                [
                    "2025-06-10 10:00:00",
                    "2025-06-10 10:00:01",
                    "2025-06-10 10:00:02",
                ]
            ),
        }
    )


class TestConvertOneSidecar:
    def test_writes_xlsx_and_sidecar(self, tmp_path, monkeypatch):
        monkeypatch.setattr(conv.nda, "read", lambda *a, **k: _fake_df())
        ndax = _make_ndax(tmp_path / "BTS83_40_7_1.ndax")
        xlsx = tmp_path / "out" / "BTS83_40_7_1.xlsx"
        result = Path(conv.convert_one(ndax, xlsx))
        assert result.exists()
        sidecar = read_sidecar(xlsx)
        assert sidecar is not None
        assert sidecar["pulse_currents"] == [30.0, 26.0, 15.0, 6.0]
        # 实测档位（裁决④ 完成性证据）：fake_df 电流仅 -30 触及声明档
        assert sidecar["observed_pulse_currents"] == [30.0]
        assert sidecar["cc_current"] == 1.0
        assert sidecar["spec_type"] == "CR2450"
        assert sidecar["test_id"] == "2818580619"

    def test_sidecar_failure_does_not_fail_conversion(self, tmp_path, monkeypatch):
        """sidecar 是增值信息：Step.xml 缺失时转换仍成功，只是没有 sidecar"""
        monkeypatch.setattr(conv.nda, "read", lambda *a, **k: _fake_df())
        ndax = tmp_path / "BTS83_40_7_1.ndax"
        with zipfile.ZipFile(ndax, "w") as zf:  # 无 Step.xml
            zf.writestr("data.ndc", b"\x00fake")
        xlsx = tmp_path / "out" / "BTS83_40_7_1.xlsx"
        assert Path(conv.convert_one(ndax, xlsx)).exists()
        assert read_sidecar(xlsx) is None


class TestConvertBatchSkipBackfill:
    def test_skip_backfills_sidecar_without_executor(self, tmp_path):
        """旧产物（xlsx 在、sidecar 无）→ skip 分支进程内回填，不进进程池"""
        ndax_dir = tmp_path / "1_ndax"
        out_dir = tmp_path / "2_xlsx"
        ndax_dir.mkdir()
        out_dir.mkdir()
        ndax = _make_ndax(ndax_dir / "a.ndax")
        xlsx = out_dir / "a.xlsx"
        xlsx.write_bytes(b"")  # 已存在 → 跳过重转
        result = conv.convert_batch(ndax_dir)
        assert result["skipped"] == ["a.ndax"]
        assert result["failed"] == []
        sidecar = read_sidecar(xlsx)
        assert sidecar is not None
        assert sidecar["pulse_currents"] == [30.0, 26.0, 15.0, 6.0]

    def test_existing_sidecar_untouched(self, tmp_path):
        import json

        ndax_dir = tmp_path / "1_ndax"
        out_dir = tmp_path / "2_xlsx"
        ndax_dir.mkdir()
        out_dir.mkdir()
        _make_ndax(ndax_dir / "a.ndax")
        xlsx = out_dir / "a.xlsx"
        xlsx.write_bytes(b"")
        from battery_analysis.utils.ndax_meta import sidecar_path_for

        marker = {"pulse_currents": [60, 30, 15, 6], "custom": True}
        sidecar_path_for(xlsx).write_text(json.dumps(marker), encoding="utf-8")
        conv.convert_batch(ndax_dir)
        assert read_sidecar(xlsx) == marker  # 不被重写覆盖


class TestConvertWorkerSkipBackfill:
    def test_worker_skip_backfills_sidecar(self, tmp_path):
        from battery_analysis.ndax.worker import ConvertWorker

        ndax_dir = tmp_path / "1_ndax"
        out_dir = tmp_path / "2_xlsx"
        ndax_dir.mkdir()
        out_dir.mkdir()
        ndax = _make_ndax(ndax_dir / "a.ndax")
        xlsx = out_dir / "a.xlsx"
        xlsx.write_bytes(b"")  # 存在且非 force → Phase1 跳过

        worker = ConvertWorker([ndax], out_dir, force=False)
        received: dict = {}
        worker.finished_signal.connect(lambda r: received.update(r))
        worker.run()  # 同步执行；跳过分支不触发进程池

        assert received["skipped"] == ["a.ndax"]
        assert read_sidecar(xlsx) is not None
