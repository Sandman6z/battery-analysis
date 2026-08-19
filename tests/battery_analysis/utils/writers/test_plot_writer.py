"""测试 plot_writer 报告图生成的数据流向"""
from unittest.mock import Mock

import pytest


@pytest.fixture
def info_image_csv(tmp_path):
    """构造 1 电池 × 1 电流档的 Info_Image.csv（每电池 4 行：跳过/header/charge/voltage）"""
    csv_path = tmp_path / "Info_Image.csv"
    csv_path.write_text(
        "Battery_1\n"
        "Battery_1\n"
        "1.0,2.0,3.0,4.0\n"
        "5.0,6.0,7.0,8.0\n",
        encoding="utf-8",
    )
    return csv_path


def test_filtered_plot_uses_filtered_data(tmp_path, info_image_csv, monkeypatch):
    """Filtered 图应绘制过滤后数据 [2]/[3]，而非原始数据 [0]/[1]"""
    from battery_analysis.utils.writers import plot_writer

    plot_calls = []

    monkeypatch.setattr(plot_writer.plt, "figure", Mock())
    monkeypatch.setattr(plot_writer.plt, "clf", Mock())
    monkeypatch.setattr(plot_writer.plt, "cla", Mock())
    monkeypatch.setattr(plot_writer.plt, "boxplot", Mock())
    monkeypatch.setattr(plot_writer.plt, "title", Mock())
    monkeypatch.setattr(plot_writer.plt, "xlabel", Mock())
    monkeypatch.setattr(plot_writer.plt, "ylabel", Mock())
    monkeypatch.setattr(plot_writer.plt, "grid", Mock())
    monkeypatch.setattr(plot_writer.plt, "gca", Mock())
    monkeypatch.setattr(plot_writer.plt, "savefig", Mock())
    mock_plot = Mock(side_effect=lambda *a, **k: plot_calls.append(a))
    monkeypatch.setattr(plot_writer.plt, "plot", mock_plot)
    monkeypatch.setattr(plot_writer.plot_utils, "set_plt_axis", Mock())
    monkeypatch.setattr(plot_writer, "MultipleLocator", lambda v: Mock())
    # 过滤后数据固定为已知值，便于断言
    monkeypatch.setattr(
        plot_writer.data_utils, "filter_data",
        lambda charge, voltage: ([[9.0, 10.0]], [[11.0, 12.0]]),
    )

    plot_writer.draw_boxplot_and_curves(
        int_current_level_num=1,
        int_voltage_level_num=1,
        list_voltage_level=[3.0],
        list_boxplot_title=["boxplot"],
        list_png_path=[str(tmp_path / "box.png")],
        list_svg_path=[str(tmp_path / "box.svg")],
        str_info_image_csv_path=str(info_image_csv),
        str_plt_name="test",
        str_unfiltered_png_path=str(tmp_path / "unf.png"),
        str_unfiltered_svg_path=str(tmp_path / "unf.svg"),
        str_filtered_png_path=str(tmp_path / "f.png"),
        str_filtered_svg_path=str(tmp_path / "f.svg"),
        list_test_info=[[0.0, 5.0]],
        list_plt_color_type=["C0"],
        int_battery_num=1,
        list_cpt=[[[100.0]]],
        max_xaxis=5.0,
    )

    # Unfiltered 图 + Filtered 图各一次 plt.plot
    assert len(plot_calls) == 2, "应恰好有 unfiltered 图与 filtered 图两次 plt.plot 调用"

    # 第一次 plt.plot 调用即 Unfiltered 图：仍应使用原始数据 [0]/[1]
    unfiltered_call = plot_calls[0]
    assert list(unfiltered_call[0]) == [1.0, 2.0, 3.0, 4.0], \
        "Unfiltered 图应使用原始 charge 数据 [0]"
    assert list(unfiltered_call[1]) == [5.0, 6.0, 7.0, 8.0], \
        "Unfiltered 图应使用原始 voltage 数据 [1]"

    # 最后一次 plt.plot 调用即 Filtered 图：应使用过滤后数据 [2]/[3]
    last_call = plot_calls[-1]
    assert list(last_call[0]) == [9.0, 10.0], "Filtered 图应使用过滤后 charge 数据 [2]"
    assert list(last_call[1]) == [11.0, 12.0], "Filtered 图应使用过滤后 voltage 数据 [3]"
