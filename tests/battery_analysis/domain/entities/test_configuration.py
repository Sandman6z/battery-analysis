# -*- coding: utf-8 -*-
"""
Configuration实体测试
"""

import pytest
from pathlib import Path
import tempfile
from battery_analysis.domain.entities.configuration import Configuration


def test_configuration_initialization():
    """测试配置实体初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 正常初始化
        config = Configuration(
            battery_type="Li-ion",
            temperature_unit="C",
            temperature_limit=60.0,
            output_path=Path(tmpdir) / "output",
            report_path=Path(tmpdir) / "reports",
            log_path=Path(tmpdir) / "logs"
        )
        
        assert config.battery_type == "Li-ion"
        assert config.temperature_unit == "C"
        assert config.temperature_limit == 60.0
        assert config.output_path == Path(tmpdir) / "output"
        assert config.report_path == Path(tmpdir) / "reports"
        assert config.log_path == Path(tmpdir) / "logs"
        assert config.language == "zh_CN"
        assert config.theme == "light"
        assert config.auto_save is True
        assert config.analysis_mode == "standard"
        assert config.calculation_precision == 4
        
        # 验证路径是否被创建
        assert config.output_path.exists()
        assert config.report_path.exists()
        assert config.log_path.exists()


def test_configuration_initialization_with_optional_fields():
    """测试配置实体初始化（包含可选字段）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Configuration(
            battery_type="Ni-MH",
            temperature_unit="F",
            temperature_limit=140.0,
            output_path=Path(tmpdir) / "output",
            report_path=Path(tmpdir) / "reports",
            log_path=Path(tmpdir) / "logs",
            language="en_US",
            theme="dark",
            auto_save=False,
            analysis_mode="advanced",
            calculation_precision=6
        )
        
        assert config.language == "en_US"
        assert config.theme == "dark"
        assert config.auto_save is False
        assert config.analysis_mode == "advanced"
        assert config.calculation_precision == 6


def test_configuration_initialization_invalid_temperature_unit():
    """测试配置实体初始化（无效的温度单位）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="温度单位必须是'C'或'F'"):
            Configuration(
                battery_type="Li-ion",
                temperature_unit="K",
                temperature_limit=333.15,
                output_path=Path(tmpdir) / "output",
                report_path=Path(tmpdir) / "reports",
                log_path=Path(tmpdir) / "logs"
            )


def test_configuration_initialization_invalid_analysis_mode():
    """测试配置实体初始化（无效的分析模式）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="分析模式必须是'standard'或'advanced'"):
            Configuration(
                battery_type="Li-ion",
                temperature_unit="C",
                temperature_limit=60.0,
                output_path=Path(tmpdir) / "output",
                report_path=Path(tmpdir) / "reports",
                log_path=Path(tmpdir) / "logs",
                analysis_mode="invalid"
            )


def test_configuration_initialization_invalid_calculation_precision():
    """测试配置实体初始化（无效的计算精度）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="计算精度不能为负数"):
            Configuration(
                battery_type="Li-ion",
                temperature_unit="C",
                temperature_limit=60.0,
                output_path=Path(tmpdir) / "output",
                report_path=Path(tmpdir) / "reports",
                log_path=Path(tmpdir) / "logs",
                calculation_precision=-1
            )
