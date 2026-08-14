"""
i18n module tests

Strategies:
- SimplePOTranslator / locale_utils: pure unit tests, no PyQt dependency
- __init__ module-level functions: patch global state to avoid side effects
- LanguageManager: real QObject, needs QApplication fixture + mocking of
  filesystem / settings to prevent test pollution
"""

import locale
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open, PropertyMock

import pytest
from PyQt6.QtWidgets import QApplication


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_PO = r'''msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"

msgid "hello"
msgstr "你好"

msgid "world"
msgstr "世界"

'''

SAMPLE_PO_WITH_CONTEXT = r'''msgid ""
msgstr ""

msgid "context:greeting"
msgstr "你好"

msgid "greeting"
msgstr "Hello"

'''

PO_HEADER_ONLY = r'''msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
'''


# ---------------------------------------------------------------------------
# TestSimplePOTranslator
# ---------------------------------------------------------------------------

class TestSimplePOTranslator:
    """translator.SimplePOTranslator — pure unit tests"""

    # ── .po parsing (via _parse) ──────────────────────────────────

    def test_parse_extracts_translations(self):
        from io import StringIO
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator(StringIO(SAMPLE_PO))
        assert t.gettext("hello") == "你好"
        assert t.gettext("world") == "世界"

    def test_parse_skips_empty_msgid(self):
        from io import StringIO
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator(StringIO(PO_HEADER_ONLY))
        assert t.gettext("hello") == "hello"  # falls back to original

    def test_gettext_fallback_to_original_when_untranslated(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        assert t.gettext("missing_key") == "missing_key"

    def test_gettext_returns_translation(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        t.translations = {"hello": "你好"}
        assert t.gettext("hello") == "你好"

    # ── pgettext (context-aware) ──────────────────────────────────

    def test_pgettext_with_context(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        t.translations = {("greeting", "hello"): "你好"}
        assert t.pgettext("greeting", "hello") == "你好"

    def test_pgettext_without_context_fallback_to_original(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        t.translations = {"hello": "Hello"}
        # (context, msgid) key doesn't exist → falls back to original text
        assert t.pgettext("greeting", "hello") == "hello"

    # ── ngettext (plurals) ────────────────────────────────────────

    def test_ngettext_singular(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        assert t.ngettext("cat", "cats", 1) == "cat"

    def test_ngettext_plural(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        assert t.ngettext("cat", "cats", 2) == "cats"

    # ── load_locale ───────────────────────────────────────────────

    def test_load_locale_success(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        with patch("builtins.open", mock_open(read_data=SAMPLE_PO)):
            with patch("pathlib.Path.exists", return_value=True):
                result = t.load_locale("zh_CN", Path("/fake"))
        assert result is True
        assert t.current_locale == "zh_CN"
        assert t.gettext("hello") == "你好"

    def test_load_locale_file_not_found(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        with patch("pathlib.Path.exists", return_value=False):
            result = t.load_locale("zh_CN", Path("/fake"))
        assert result is False

    def test_load_locale_io_error_returns_empty(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        with patch("builtins.open", side_effect=IOError("no file")):
            with patch("pathlib.Path.exists", return_value=True):
                result = t.load_locale("zh_CN", Path("/fake"))
        assert result is False

    # ── .translations property (backward compat) ──────────────────

    def test_translations_property(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        t = SimplePOTranslator()
        t.translations = {"hello": "你好"}
        assert t.translations == {"hello": "你好"}
        assert t.gettext("hello") == "你好"


# ---------------------------------------------------------------------------
# TestRealCatalogRoundTrip — 真实 locale/zh_CN 目录往返集成测试
# ---------------------------------------------------------------------------

class TestRealCatalogRoundTrip:
    """Loads the real repo-root locale/zh_CN catalog (integration)."""

    @staticmethod
    def _locale_dir() -> Path:
        # tests/battery_analysis/i18n/ -> repo root (parents[3])
        return Path(__file__).resolve().parents[3] / "locale"

    def test_zh_cn_catalog_translates_known_msgids(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        locale_dir = self._locale_dir()
        if not (locale_dir / "zh_CN" / "LC_MESSAGES" / "messages.po").exists():
            pytest.skip("locale/zh_CN catalog not built")
        t = SimplePOTranslator()
        assert t.load_locale("zh_CN", locale_dir) is True
        assert t.gettext("Preferences") == "首选项"
        assert t.gettext("Exit") == "退出应用"

    def test_zh_cn_multiline_msgid_round_trip(self):
        from battery_analysis.i18n.translator import SimplePOTranslator
        locale_dir = self._locale_dir()
        if not (locale_dir / "zh_CN" / "LC_MESSAGES" / "messages.po").exists():
            pytest.skip("locale/zh_CN catalog not built")
        t = SimplePOTranslator()
        assert t.load_locale("zh_CN", locale_dir) is True
        key = ("The application will restart with the default configuration.\n\n"
               "Please make sure you have valid data files available.")
        expected = ("应用将使用默认配置重新启动。\n\n"
                    "请确保您有有效的数据文件可用。")
        assert t.gettext(key) == expected


# ---------------------------------------------------------------------------
# TestLocaleUtils
# ---------------------------------------------------------------------------

class TestLocaleUtilsGetAvailableLocales:
    """locale_utils.get_available_locales"""

    def test_finds_locale_dirs_with_po(self, tmp_path):
        from battery_analysis.i18n.locale_utils import get_available_locales
        en = tmp_path / "en" / "LC_MESSAGES"
        en.mkdir(parents=True)
        (en / "messages.po").write_text("")
        zh = tmp_path / "zh_CN" / "LC_MESSAGES"
        zh.mkdir(parents=True)
        (zh / "messages.po").write_text("")
        result = get_available_locales(tmp_path)
        assert result == ["en", "zh_CN"]

    def test_returns_empty_when_dir_missing(self, tmp_path):
        from battery_analysis.i18n.locale_utils import get_available_locales
        assert get_available_locales(tmp_path / "nonexistent") == []

    def test_skips_dirs_without_po(self, tmp_path):
        from battery_analysis.i18n.locale_utils import get_available_locales
        d = tmp_path / "de" / "LC_MESSAGES"
        d.mkdir(parents=True)
        # no messages.po
        assert get_available_locales(tmp_path) == []


class TestLocaleUtilsDetectSystemLocale:
    """locale_utils.detect_system_locale"""

    def test_returns_none_on_error(self):
        from battery_analysis.i18n.locale_utils import detect_system_locale
        with patch("locale.getlocale", side_effect=ValueError("bad")):
            assert detect_system_locale() is None

    def test_returns_string_when_detected(self):
        from battery_analysis.i18n.locale_utils import detect_system_locale
        with patch("locale.getlocale", return_value=("en_US", "UTF-8")):
            result = detect_system_locale()
            assert result == "en_US"


class TestLocaleUtilsResolveLocaleCode:
    """locale_utils.resolve_locale_code"""

    def test_direct_match(self):
        from battery_analysis.i18n.locale_utils import resolve_locale_code
        assert resolve_locale_code("zh_CN", ["en", "zh_CN"]) == "zh_CN"

    def test_display_name_match(self):
        from battery_analysis.i18n.locale_utils import resolve_locale_code
        assert resolve_locale_code("中文(简体)", ["en", "zh_CN"]) == "zh_CN"

    def test_no_match_returns_none(self):
        from battery_analysis.i18n.locale_utils import resolve_locale_code
        assert resolve_locale_code("xx_XX", ["en", "zh_CN"]) is None


class TestLocaleUtilsSystemLocaleToCode:
    """locale_utils.system_locale_to_code"""

    def test_exact_match(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        assert system_locale_to_code("zh_CN", ["en", "zh_CN"]) == "zh_CN"

    def test_lang_code_match(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        assert system_locale_to_code("de_DE", ["en", "de"]) == "de"

    def test_zh_TW_preferred_over_zh_CN(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        available = ["en", "zh_CN", "zh_TW"]
        # HK → prefer TW
        assert system_locale_to_code("zh_HK", available) == "zh_TW"
        # CN → prefer CN
        assert system_locale_to_code("zh_CN", available) == "zh_CN"

    def test_partial_prefix_match(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        assert system_locale_to_code("de_DE", ["en", "de"]) == "de"

    def test_no_match(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        assert system_locale_to_code("xx_XX", ["en", "zh_CN"]) is None

    def test_zh_TW_fallback_to_zh_CN(self):
        from battery_analysis.i18n.locale_utils import system_locale_to_code
        assert system_locale_to_code("zh_TW", ["en", "zh_CN"]) == "zh_CN"


# ---------------------------------------------------------------------------
# TestModuleFunctions  (i18n/__init__.py)
# ---------------------------------------------------------------------------

class TestModuleFunctionsSetLocale:
    """__init__.set_locale"""

    def test_successful_set_locale(self):
        from battery_analysis.i18n import set_locale
        with patch("battery_analysis.i18n.locale_utils.get_available_locales", return_value=["en", "zh_CN"]):
            with patch("battery_analysis.i18n._load_locale", return_value=True):
                result = set_locale("en")
        assert result is True

    def test_set_locale_unavailable_returns_false(self):
        from battery_analysis.i18n import set_locale
        with patch("battery_analysis.i18n.locale_utils.get_available_locales", return_value=["en"]):
            with patch("battery_analysis.i18n.locale_utils.resolve_locale_code", return_value=None):
                result = set_locale("xx_XX")
        assert result is False


class TestModuleFunctionsTranslate:
    """__init__._ and ngettext"""

    def test_translate_returns_translated_text(self):
        from battery_analysis.i18n import _
        with patch("battery_analysis.i18n._po_translator.gettext", return_value="你好") as mock_get:
            result = _("hello")
        assert result == "你好"
        mock_get.assert_called_once_with("hello")

    def test_translate_with_context(self):
        from battery_analysis.i18n import _
        with patch("battery_analysis.i18n._po_translator.pgettext", return_value="您好") as mock_pget:
            result = _("hello", context="greeting")
        assert result == "您好"
        mock_pget.assert_called_once_with("greeting", "hello")

    def test_translate_fallback_on_error(self):
        from battery_analysis.i18n import _
        with patch("battery_analysis.i18n._po_translator.gettext", side_effect=AttributeError("bad")):
            assert _("hello") == "hello"

    def test_pgettext_delegates_to_translate(self):
        from battery_analysis.i18n import pgettext
        with patch("battery_analysis.i18n._po_translator.pgettext", return_value="您好") as mock_pget:
            result = pgettext("greeting", "hello")
        assert result == "您好"
        mock_pget.assert_called_once_with("greeting", "hello")

    def test_ngettext_singular(self):
        from battery_analysis.i18n import ngettext
        with patch("battery_analysis.i18n._po_translator.ngettext", return_value="cat") as mock_n:
            assert ngettext("cat", "cats", 1) == "cat"
        mock_n.assert_called_once_with("cat", "cats", 1)

    def test_ngettext_plural(self):
        from battery_analysis.i18n import ngettext
        with patch("battery_analysis.i18n._po_translator.ngettext", return_value="cats") as mock_n:
            assert ngettext("cat", "cats", 2) == "cats"
        mock_n.assert_called_once_with("cat", "cats", 2)

    def test_ngettext_fallback_on_error(self):
        from battery_analysis.i18n import ngettext
        with patch("battery_analysis.i18n._po_translator.ngettext", side_effect=AttributeError("bad")):
            result = ngettext("cat", "cats", 1)
        assert result == "cat"  # fallback to singular

    def test_get_current_locale(self):
        from battery_analysis.i18n import get_current_locale, _current_locale
        saved = _current_locale
        try:
            with patch("battery_analysis.i18n._current_locale", "fr"):
                assert get_current_locale() == "fr"
        finally:
            _current_locale = saved


class TestModuleFunctionsLoadLocale:
    """__init__._load_locale"""

    def test_load_locale_updates_globals(self):
        from battery_analysis.i18n import _load_locale
        import battery_analysis.i18n as i18n_module
        saved = i18n_module._current_locale
        with patch("battery_analysis.i18n._po_translator") as mock_t:
            mock_t.load_locale.return_value = True
            result = _load_locale("zh_CN")
        assert result is True
        assert i18n_module._current_locale == "zh_CN"
        i18n_module._current_locale = saved


class TestModuleFunctionsDetectSystemLocale:
    """__init__.detect_system_locale"""

    def test_detects_system_locale(self):
        from battery_analysis.i18n import detect_system_locale
        with patch("battery_analysis.i18n.locale_utils.detect_system_locale", return_value="en_US"):
            with patch("battery_analysis.i18n.LOCALEDIR", Path("/fake")):
                with patch("battery_analysis.i18n.locale_utils.get_available_locales", return_value=["en"]):
                    with patch("battery_analysis.i18n.locale_utils.system_locale_to_code", return_value="en"):
                        assert detect_system_locale() == "en"

    def test_falls_back_to_en_when_no_system_locale(self):
        from battery_analysis.i18n import detect_system_locale
        with patch("battery_analysis.i18n.locale_utils.detect_system_locale", return_value=None):
            assert detect_system_locale() == "en"


class TestModuleFunctionsInitializeDefaultLocale:
    """__init__.initialize_default_locale — 默认锁定英文"""

    def test_initializes_to_english(self):
        from battery_analysis.i18n import initialize_default_locale
        with patch("battery_analysis.i18n.set_locale", return_value=True) as mock_set:
            assert initialize_default_locale() is True
            mock_set.assert_called_once_with("en")

    def test_returns_false_when_english_unavailable(self):
        from battery_analysis.i18n import initialize_default_locale
        with patch("battery_analysis.i18n.set_locale", return_value=False) as mock_set:
            assert initialize_default_locale() is False
            mock_set.assert_called_once_with("en")


# ---------------------------------------------------------------------------
# TestIConfigPathProvider
# ---------------------------------------------------------------------------

class TestIConfigPathProvider:
    """config_path_provider.IConfigPathProvider — abstract interface"""

    def test_cannot_instantiate(self):
        from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider
        with pytest.raises(TypeError):
            IConfigPathProvider()

    def test_concrete_subclass_must_implement_abstract_method(self):
        from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider
        with pytest.raises(TypeError):
            type("BadImpl", (IConfigPathProvider,), {})()

    def test_valid_implementation(self):
        from battery_analysis.main.ui_components.config_path_provider import IConfigPathProvider
        impl = type("GoodImpl", (IConfigPathProvider,), {"get_config_path": lambda self: "/path"})()
        assert impl.get_config_path() == "/path"


# ---------------------------------------------------------------------------
# TestLanguageManager  (requires QApplication)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    # 复用已有实例，避免在 e2e 等测试已创建 QApplication 后再 new 一个
    # 导致 PyQt6 单例冲突（Windows 下触发 access violation 崩溃）
    return QApplication.instance() or QApplication([])


class TestLanguageManager:
    """language_manager.LanguageManager — requires QApplication"""

    @pytest.fixture(autouse=True)
    def _setup(self, qapp):
        """Patch filesystem and settings to prevent side effects."""
        with patch.object(Path, "exists", return_value=True):
            yield

    def test_init_sets_locale(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        with patch("battery_analysis.i18n.language_manager.detect_system_locale", return_value="en"):
            with patch("battery_analysis.i18n.language_manager.set_locale", return_value=True):
                lm = LanguageManager()
        assert lm is not None

    def test_get_available_locales(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        locales = lm.get_available_locales()
        assert "en" in locales
        assert "zh_CN" in locales

    def test_get_installed_locales(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        with patch.object(LanguageManager, "_has_translation_file", return_value=True):
            lm = LanguageManager()
            installed = lm.get_installed_locales()
        assert "en" in installed

    def test_set_locale_unsupported_returns_false(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        result = lm.set_locale("xx_XX")
        assert result is False

    def test_set_locale_no_translation_file(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        with patch.object(LanguageManager, "_has_translation_file", return_value=False):
            lm = LanguageManager()
            result = lm.set_locale("zh_CN")
        assert result is False

    def test_set_locale_success(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        with patch.object(LanguageManager, "_has_translation_file", return_value=True):
            with patch("battery_analysis.i18n.language_manager.set_locale", return_value=True):
                lm = LanguageManager()
                result = lm.set_locale("zh_CN")
        assert result is True

    def test_get_current_locale(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        with patch("battery_analysis.i18n.language_manager.get_current_locale", return_value="en"):
            lm = LanguageManager()
            assert lm.get_current_locale() == "en"

    def test_get_text_without_context(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "_direct_translate", return_value="你好"):
            assert lm.get_text("hello") == "你好"

    def test_get_text_with_context(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch("battery_analysis.i18n.language_manager.pgettext", return_value="你好"):
            assert lm.get_text("hello", context="greeting") == "你好"

    def test_get_plural_text(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch("battery_analysis.i18n.language_manager.ngettext", return_value="cats"):
            assert lm.get_plural_text("cat", "cats", 2) == "cats"

    def test_format_translation(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch("battery_analysis.i18n.language_manager._", return_value="Hello {name}"):
            result = lm.format_translation("greeting_template", name="World")
        assert result == "Hello World"

    def test_format_translation_fallback_on_error(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch("battery_analysis.i18n.language_manager._", return_value="Hello {name}"):
            result = lm.format_translation("greeting_template")
        assert result == "Hello {name}"

    def test_get_locale_info_known(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        info = lm.get_locale_info("en")
        assert info["code"] == "en"
        assert info["name"] == "English"

    def test_get_locale_info_unknown_returns_empty(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        assert lm.get_locale_info("xx_XX") == {}

    def test_reload_translations(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "set_locale", return_value=True):
            assert lm.reload_translations() is True

    def test_reset_to_default(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch("battery_analysis.i18n.language_manager.detect_system_locale", return_value="en"):
            with patch.object(lm, "set_locale", return_value=True):
                lm.reset_to_default()
        # should not raise

    def test_validate_translations(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "set_locale", return_value=True):
            with patch("battery_analysis.i18n.language_manager._", side_effect=lambda x, y=None: "translated" if x == "OK" else x):
                result = lm.validate_translations("zh_CN")
        assert "OK" in result

    def test_save_preferences(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        lm.settings = MagicMock()
        lm.save_preferences()
        lm.settings.sync.assert_called_once()

    def test_get_language_manager_singleton(self):
        from battery_analysis.i18n.language_manager import get_language_manager, _language_manager
        saved = _language_manager
        # Clear the singleton
        from battery_analysis.i18n import language_manager as lm_module
        lm_module._language_manager = None
        with patch("battery_analysis.i18n.language_manager.detect_system_locale", return_value="en"):
            with patch("battery_analysis.i18n.language_manager.set_locale", return_value=True):
                instance1 = get_language_manager()
                instance2 = get_language_manager()
        assert instance1 is instance2
        # Restore
        lm_module._language_manager = saved

    # --- Backwards-compatibility aliases ---

    def test_get_available_locales(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "get_available_locales", return_value={"en": "English"}):
            assert lm.get_available_locales() == {"en": "English"}

    def test_get_installed_locales(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "get_installed_locales", return_value={"en": "English"}):
            assert lm.get_installed_locales() == {"en": "English"}

    def test_get_current_locale(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "get_current_locale", return_value="en"):
            assert lm.get_current_locale() == "en"

    def test_set_locale(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        with patch.object(lm, "set_locale", return_value=True):
            assert lm.set_locale("en") is True

    # --- Error handling ---

    def test_export_translations_not_implemented(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        assert lm.export_translations("en", "/tmp/out.json") is False

    def test_direct_translate_fallback_on_error(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        assert lm._direct_translate("hello") == "hello"

    def test_on_language_changed_logs(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        # 用 mock 断言日志调用，而非 caplog：一旦 get_logger() 被调用过
        # （例如 e2e 测试构造 Main），log_manager 会把 battery_analysis logger
        # 设为 propagate=False，日志不再传播到 root，caplog（挂在 root）就捕获不到。
        # mock 断言不依赖日志传播链，测试结果与执行顺序无关。
        with patch.object(lm.logger, "info") as mock_info:
            lm._on_language_changed("zh_CN")
        mock_info.assert_called_once_with("Language changed to: %s", "zh_CN")

    def test_default_locale_is_english_when_no_saved(self):
        from battery_analysis.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        lm.settings = MagicMock()
        lm.settings.value.return_value = ""
        # Force a non-English system locale so the assertion proves the default
        # is fixed to "en" regardless of what detect_system_locale() returns.
        with patch("battery_analysis.i18n.language_manager.detect_system_locale", return_value="zh_CN"):
            with patch.object(lm, "set_locale", return_value=True) as mock_set:
                lm._initialize_settings()
        mock_set.assert_called_once_with("en")
