import zipfile

import pytest

from battery_analysis.ndax.reader import (
    _xml_root,
    profile_levels,
    pulse_levels,
    recipe_levels,
    recipe_temperature,
)


def test_recipe_levels_from_gb2312_ndax(tmp_path):
    xml = '<?xml version="1.0" encoding="GB2312"?><root><Step_Info><Step4><PulseData Count="5"><Pulse1 Value="0"/><Pulse2 Value="-30"/><Pulse3 Value="-26"/><Pulse4 Value="0"/><Pulse5 Value="-6"/></PulseData></Step4></Step_Info></root>'
    path = tmp_path / "channel.ndax"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Step.xml", xml.encode("gb2312"))
    assert recipe_levels(path) == [30, 26, 6]
    assert pulse_levels(_xml_root(xml.encode("gb2312"))) == [30, 26, 6]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Step.xml", xml.replace('Count="5"', 'Count="6"').encode("gb2312"))
    with pytest.raises(ValueError, match="Count"):
        recipe_levels(path)


@pytest.mark.parametrize("name, expected", [
    ("CR2450_QATest_Freezer.xml", "Freezer Temperature"),
    ("CR2450_fReEzEr.xml", "Freezer Temperature"),
    ("CR2450_QATest.xml", "Room Temperature"),
    ("常温.xml", "Room Temperature"),
])
def test_temperature_from_embedded_step_name(tmp_path, name, expected):
    # 外部 NDAX 文件名不能影响内部配方判断。
    path = tmp_path / "misleading_freezer.ndax"
    text = f'<?xml version="1.0" encoding="GB2312"?><root><config><TestInfo StepName="{name}"/></config></root>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("TestInfo.xml", text.encode("gb2312"))
    assert recipe_temperature(path) == expected


@pytest.mark.parametrize("text", [None, "<root/>", '<root><TestInfo StepName=" "/></root>', "<bad"])
def test_missing_or_invalid_temperature_source_is_rejected(tmp_path, text):
    path = tmp_path / "channel.ndax"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("TestInfo.xml" if text is not None else "other.xml", text or "")
    with pytest.raises(ValueError, match=r"TestInfo\.xml"):
        recipe_temperature(path)


def test_profile_level_mismatch_is_exact(tmp_path):
    profile = tmp_path / "profile.xml"
    profile.write_text('<root><Step_Info><Step4><PulseData Count="2"><Pulse1 Value="-30"/><Pulse2 Value="-26.01"/></PulseData></Step4></Step_Info></root>', encoding="utf-8")
    assert profile_levels(profile) == [30, 26.01]
    assert profile_levels(profile) != [30.0, 26.0]
