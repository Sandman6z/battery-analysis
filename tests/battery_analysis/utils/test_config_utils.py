from unittest.mock import patch

from battery_analysis.utils.config_utils import find_config_file


class TestConfigUtils:
    def test_find_config_file(self):
        """测试查找配置文件函数"""
        # 测试函数调用是否正常
        result = find_config_file(file_name="test.ini", use_cache=False)
        # 函数应该返回一个字符串或None
        assert result is None or isinstance(result, str)

    def test_clear_config_cache_resets_custom_path_cache(self):
        """回归测试 I-1：clear_config_cache 必须清除自定义路径缓存

        否则 _get_custom_config_path() 会命中旧缓存而忽略 QSettings 新值
        （修改/清空自定义配置路径后无法生效）
        """
        from battery_analysis.utils.config_utils import (
            _get_custom_config_path,
            clear_config_cache,
            clear_custom_config_path,
        )

        # 确保缓存干净
        clear_custom_config_path()

        with patch("PyQt6.QtCore.QSettings") as mock_settings_cls:
            # 首次：无缓存，从 QSettings 读取并写入缓存
            mock_settings_cls.return_value.value.return_value = "path_A"
            assert _get_custom_config_path() == "path_A"

            # 修改 QSettings 返回值，模拟用户更改/清空配置路径
            mock_settings_cls.return_value.value.return_value = "path_B"
            # 未清缓存时命中旧缓存，新值被忽略（回归场景）
            assert _get_custom_config_path() == "path_A"

            # 清缓存后应重新读 QSettings 并返回新值
            clear_config_cache()
            assert _get_custom_config_path() == "path_B"
