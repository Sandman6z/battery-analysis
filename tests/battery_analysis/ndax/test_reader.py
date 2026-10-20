import zipfile

import pytest

from battery_analysis.ndax.reader import _xml_root, profile_levels, pulse_levels, recipe_levels


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


def test_profile_level_mismatch_is_exact(tmp_path):
    profile = tmp_path / "profile.xml"
    profile.write_text('<root><Step_Info><Step4><PulseData Count="2"><Pulse1 Value="-30"/><Pulse2 Value="-26.01"/></PulseData></Step4></Step_Info></root>', encoding="utf-8")
    assert profile_levels(profile) == [30, 26.01]
    assert profile_levels(profile) != [30.0, 26.0]
