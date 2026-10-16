import json
from unittest.mock import Mock

from battery_analysis.main.managers.analysis_runner import AnalysisRunner


class TestAnalysisRunner:
    def setup_method(self):
        self.main_window = Mock()
        self.runner = AnalysisRunner(self.main_window)

    def test_init(self):
        assert self.runner.main_window == self.main_window

    def test_run_analysis(self):
        self.main_window.table_manager = Mock()
        self.main_window.table_manager.save_table = Mock()
        self.main_window.ui_manager = Mock()
        self.main_window.ui_manager.init_widgetcolor = Mock()
        self.runner.run_analysis()
        self.main_window.table_manager.save_table.assert_called_once()
        self.main_window.ui_manager.init_widgetcolor.assert_called_once()


# ---------------------------------------------------------------------------
# profile 与 ndax 档位校验闸门（会议裁决①③④）
# ---------------------------------------------------------------------------

import battery_analysis.main.managers.analysis_runner as ar  # noqa: E402
from battery_analysis.utils.ndax_meta import sidecar_path_for  # noqa: E402

PROFILE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<config type="Step File" version="17" date="20250610100145">
  <Step_Info Num="6">
    <Step4 Step_ID="4" Step_Type="16">
      <PulseData Pulse_Mode="1">
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
"""


def _make_env(
    tmp_path, levels_per_file, profile_levels=(30, 26, 15, 6), observed=None, medians=None
):
    """构造 input_dir（xlsx+sidecar）与 profile xml；返回 (runner, mw, profile_path)。"""
    input_dir = tmp_path / "2_xlsx"
    input_dir.mkdir(exist_ok=True)
    for idx, levels in enumerate(levels_per_file):
        xlsx = input_dir / f"BTS83_40_7_{idx + 1}.xlsx"
        xlsx.write_bytes(b"")
        if levels is not None:
            payload = {"schema_version": 1, "pulse_currents": list(levels)}
            if observed is not None:
                payload["observed_pulse_currents"] = list(observed)
            if medians is not None:
                payload["observed_pulse_medians"] = dict(medians)
            sidecar_path_for(xlsx).write_text(json.dumps(payload), encoding="utf-8")
    profile_path = tmp_path / "profile.xml"
    if profile_levels is not None:
        profile_path.write_text(PROFILE_XML, encoding="utf-8")

    mw = Mock()
    mw.lineEdit_InputPath.text.return_value = str(input_dir)
    if profile_levels is None:
        mw.lineEdit_TestProfile.text.return_value = ""
    else:
        mw.lineEdit_TestProfile.text.return_value = str(profile_path)
    runner = ar.AnalysisRunner(mw)
    return runner, mw, profile_path


class _FakeCriticalBox:
    """只拦截 QMessageBox.critical 的轻量替身。"""

    calls: list = []

    @classmethod
    def critical(cls, parent, title, body):
        cls.calls.append((title, body))


class _FakeSettings:
    """QSettings 替身：内存字典模拟 validation/profile_disclaimer_version 记忆。"""

    store: dict = {}

    def value(self, key):
        return self.store.get(key)

    def setValue(self, key, value):
        self.store[key] = value


def _patch_disclaimer(monkeypatch, infos):
    """拦截声明弹框的信息框与 QSettings，返回 (infos, settings_store)。"""
    monkeypatch.setattr(ar.QC, "QSettings", lambda: _FakeSettings())
    monkeypatch.setattr(ar.QW.QMessageBox, "information", lambda *a: infos.append(a))
    return _FakeSettings.store


class TestProfileValidationGate:
    def setup_method(self):
        _FakeCriticalBox.calls = []

    def test_drift_shows_yellow_warning_and_passes(self, tmp_path, monkeypatch):
        """裁决②：match 但实测漂移超阈值 → 黄警 + 放行留痕。"""
        runner, mw, _ = _make_env(
            tmp_path,
            levels_per_file=[[30, 26, 15, 6]],
            medians={"30.0": 30.8, "26.0": 26.1},
        )
        warnings = []
        monkeypatch.setattr(
            ar.QW.QMessageBox,
            "warning",
            lambda *a: warnings.append(a),
        )
        assert runner._run_profile_validation() is True
        assert len(warnings) == 1
        assert "30 mA" in warnings[0][2]  # 漂移档位出现在文案
        assert mw.profile_validation["measured_drift"] == {"30": 0.8}
        assert mw.profile_validation["decision"] == "proceed"

    def test_no_drift_no_warning(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(
            tmp_path,
            levels_per_file=[[30, 26, 15, 6]],
            medians={"30.0": 30.4},
        )
        warnings = []
        monkeypatch.setattr(
            ar.QW.QMessageBox,
            "warning",
            lambda *a: warnings.append(a),
        )
        assert runner._run_profile_validation() is True
        assert warnings == []
        assert "measured_drift" not in mw.profile_validation

    def test_no_sidecar_passes_old_chain(self, tmp_path):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[None])
        assert runner._run_profile_validation() is True
        assert mw.profile_validation is None

    def test_no_profile_passes_without_record(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(
            tmp_path, levels_per_file=[[30, 26, 15, 6]], profile_levels=None
        )
        store = _patch_disclaimer(monkeypatch, [])
        assert runner._run_profile_validation() is True
        assert mw.profile_validation is None
        assert store["validation/profile_disclaimer_version"] == "2026.10"

    def test_match_passes_with_record(self, tmp_path):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[[30, 26, 15, 6]])
        assert runner._run_profile_validation() is True
        assert mw.profile_validation["result"] == "match"
        assert mw.profile_validation["decision"] == "proceed"
        assert mw.profile_validation["policy_version"] == "2026.10"

    def test_batch_inconsistent_blocks_without_override(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(
            tmp_path, levels_per_file=[[60, 30, 15, 6], [30, 26, 15, 6]]
        )
        monkeypatch.setattr(ar.QW.QMessageBox, "critical", _FakeCriticalBox.critical)
        asked = []
        monkeypatch.setattr(
            runner, "_ask_override", lambda *a: asked.append(a) or True
        )
        assert runner._run_profile_validation() is False
        assert asked == []  # 裁决③：无放行选项
        assert mw.profile_validation is None
        assert _FakeCriticalBox.calls  # 已弹硬阻断框
        mw.pushButton_Run.setEnabled.assert_called_with(True)

    def test_value_mismatch_abort_returns_false(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[[60, 30, 15, 6]])
        monkeypatch.setattr(runner, "_ask_override", lambda *a: False)
        assert runner._run_profile_validation() is False
        assert mw.profile_validation is None

    def test_value_mismatch_accept_records_override(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[[60, 30, 15, 6]])
        monkeypatch.setattr(runner, "_ask_override", lambda *a: True)
        assert runner._run_profile_validation() is True
        assert mw.profile_validation["result"] == "value_mismatch"
        assert mw.profile_validation["decision"] == "override_accepted"

    def test_count_excess_offers_override(self, tmp_path, monkeypatch):
        # ndax 4 档 > profile：改 profile 为 3 档
        runner, mw, profile_path = _make_env(
            tmp_path, levels_per_file=[[60, 30, 15, 6]]
        )
        profile_path.write_text(
            PROFILE_XML.replace('<Pulse8 Value="-6" Time="5000"/>', ""),
            encoding="utf-8",
        )
        asked = []
        monkeypatch.setattr(
            runner, "_ask_override", lambda *a: asked.append(a) or True
        )
        assert runner._run_profile_validation() is True
        assert len(asked) == 1
        assert mw.profile_validation["mismatch_type"] == "level_count_mismatch_excess"
        assert mw.profile_validation["decision"] == "override_accepted"

    def test_count_fewer_complete_offers_override(self, tmp_path, monkeypatch):
        # ndax 3 档 < profile 4 档，observed 覆盖 ndax 全部声明 → complete
        runner, mw, _ = _make_env(
            tmp_path,
            levels_per_file=[[30, 15, 6]],
            observed=[30, 15, 6],
        )
        monkeypatch.setattr(runner, "_ask_override", lambda *a: True)
        assert runner._run_profile_validation() is True
        assert mw.profile_validation["mismatch_type"] == "level_count_mismatch_complete"

    def test_count_fewer_truncated_blocks(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(
            tmp_path,
            levels_per_file=[[30, 15, 6]],
            observed=[30, 15],  # 声明 6 档未实测 → truncated
        )
        monkeypatch.setattr(ar.QW.QMessageBox, "critical", _FakeCriticalBox.critical)
        assert runner._run_profile_validation() is False
        assert mw.profile_validation is None
        assert _FakeCriticalBox.calls

    def test_missing_evidence_blocks(self, tmp_path, monkeypatch):
        # 旧 sidecar：有 pulse_currents 无 observed → 从严
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[[30, 15, 6]])
        monkeypatch.setattr(ar.QW.QMessageBox, "critical", _FakeCriticalBox.critical)
        assert runner._run_profile_validation() is False
        assert mw.profile_validation is None

    def test_no_sidecar_ignores_profile_field(self, tmp_path):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[None])
        del mw.lineEdit_TestProfile  # 无 sidecar 时不需要 profile 字段
        assert runner._run_profile_validation() is True


class TestNoProfileDisclaimer:
    """无 profile 声明弹框：只提示一次，按政策版本记忆（裁决⑤）。"""

    def setup_method(self):
        _FakeSettings.store = {}

    def test_first_run_shows_disclaimer_and_remembers(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(
            tmp_path, levels_per_file=[[30, 26, 15, 6]], profile_levels=None
        )
        infos = []
        store = _patch_disclaimer(monkeypatch, infos)
        assert runner._run_profile_validation() is True
        assert len(infos) == 1
        assert store["validation/profile_disclaimer_version"] == "2026.10"
        assert mw.profile_validation is None  # 声明放行不写决策留痕

    def test_second_run_skips_disclaimer(self, tmp_path, monkeypatch):
        # 已声明过（版本一致）→ 不再弹
        _FakeSettings.store = {"validation/profile_disclaimer_version": "2026.10"}
        runner, mw, _ = _make_env(
            tmp_path, levels_per_file=[[30, 26, 15, 6]], profile_levels=None
        )
        infos = []
        _patch_disclaimer(monkeypatch, infos)
        assert runner._run_profile_validation() is True
        assert infos == []

    def test_stale_version_shows_disclaimer_again(self, tmp_path, monkeypatch):
        # 政策版本升级 → 重新声明一次
        _FakeSettings.store = {"validation/profile_disclaimer_version": "2025.01"}
        runner, mw, _ = _make_env(
            tmp_path, levels_per_file=[[30, 26, 15, 6]], profile_levels=None
        )
        infos = []
        store = _patch_disclaimer(monkeypatch, infos)
        assert runner._run_profile_validation() is True
        assert len(infos) == 1
        assert store["validation/profile_disclaimer_version"] == "2026.10"

    def test_profile_present_never_shows_disclaimer(self, tmp_path, monkeypatch):
        runner, mw, _ = _make_env(tmp_path, levels_per_file=[[30, 26, 15, 6]])
        infos = []
        _patch_disclaimer(monkeypatch, infos)
        assert runner._run_profile_validation() is True
        assert infos == []
        assert mw.profile_validation["result"] == "match"


class TestAskOverrideDialog:
    """裁决① 两按钮弹窗：[中止]（默认焦点）+[以 ndax 档位为准继续]。"""

    def _patch_box(self, monkeypatch, click):
        real = ar.QW.QMessageBox

        class FakeBox:
            Icon = real.Icon
            ButtonRole = real.ButtonRole
            instances: list = []

            def __init__(self, parent=None):
                self._buttons = []
                self._clicked = None
                self._default = None
                FakeBox.instances.append(self)

            def setIcon(self, *a):
                pass

            def setWindowTitle(self, *a):
                pass

            def setText(self, *a):
                pass

            def setInformativeText(self, *a):
                pass

            def setDetailedText(self, *a):
                pass

            def addButton(self, text, role):
                button = type("Btn", (), {"text": text, "role": role})()
                self._buttons.append(button)
                return button

            def setDefaultButton(self, button):
                self._default = button

            def exec(self):
                if click == "abort":
                    self._clicked = self._buttons[0]
                elif click == "continue":
                    self._clicked = self._buttons[1]
                # None → Esc：clickedButton 保持 None

            def clickedButton(self):
                return self._clicked

        monkeypatch.setattr(ar.QW, "QMessageBox", FakeBox, raising=False)
        return FakeBox

    def _runner(self):
        return ar.AnalysisRunner(Mock()), Mock()

    def test_two_buttons_abort_default(self, monkeypatch):
        FakeBox = self._patch_box(monkeypatch, click="abort")
        runner, _ = self._runner()
        record = {"result": "value_mismatch"}
        assert runner._ask_override([30, 26], [60, 30], record) is False
        box = FakeBox.instances[0]
        assert len(box._buttons) == 2
        assert box._buttons[0].text == "Abort"
        assert box._default is box._buttons[0]  # 默认焦点=中止

    def test_continue_returns_true(self, monkeypatch):
        FakeBox = self._patch_box(monkeypatch, click="continue")
        runner, _ = self._runner()
        assert runner._ask_override([30, 26], [60, 30], {"result": "value_mismatch"}) is True
        assert FakeBox.instances[0]._buttons[1].role is FakeBox.ButtonRole.AcceptRole

    def test_escape_returns_false(self, monkeypatch):
        self._patch_box(monkeypatch, click=None)
        runner, _ = self._runner()
        assert runner._ask_override([30, 26], [60, 30], {"result": "value_mismatch"}) is False


class TestProfileValidationPipeline:
    def test_update_controller_context_carries_record(self):
        mw = Mock()
        runner = ar.AnalysisRunner(mw)
        record = {"result": "match", "decision": "proceed", "policy_version": "2026.10"}
        mw.profile_validation = record
        runner._update_controller_context("ti")
        controller = mw._get_controller.return_value
        assert controller.profile_validation == record
