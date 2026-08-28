"""Simple .po file translator — built on Python standard library gettext"""

import re
import gettext
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


# ── Plural-formula compiler ────────────────────────────────────────


# 已知 Plural-Forms 公式表（键 = .po 头解析出的公式字符串，已 strip）。
# 覆盖当前仓库实际使用的 en/zh_CN 公式，以及常见 gettext 公式变体
# （含 GNU 规范括号形式，如 fr 的 (n > 1)、ru 首条件带括号的嵌套三元）。
# 未知公式降级为单数形式（lambda _n: 0），与旧 eval 失败 fallback 语义一致。
_PLURAL_FORMULA_TABLE: Dict[str, Callable[[int], int]] = {
    # nplurals=1（zh_TW/ja/ko）
    "0": lambda _n: 0,
    # nplurals=2 常见形式（en/zh_CN/de/es/it/pt/hi 及带括号变体）
    "n != 1": lambda n: 0 if n == 1 else 1,
    "(n != 1)": lambda n: 0 if n == 1 else 1,
    # nplurals=2, plural=(n > 1)（fr，含 GNU 规范括号变体）
    "n > 1": lambda n: 0 if n <= 1 else 1,
    "(n > 1)": lambda n: 0 if n <= 1 else 1,
    # nplurals=3（ru）——俄语式嵌套三元（含 GNU 规范首条件带括号变体）
    "n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2":
        lambda n: (0 if n % 10 == 1 and n % 100 != 11
                   else 1 if n % 10 >= 2 and n % 10 <= 4
                   and (n % 100 < 10 or n % 100 >= 20) else 2),
    "(n%10==1 && n%100!=11) ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2":
        lambda n: (0 if n % 10 == 1 and n % 100 != 11
                   else 1 if n % 10 >= 2 and n % 10 <= 4
                   and (n % 100 < 10 or n % 100 >= 20) else 2),
    # nplurals=6（ar）——阿拉伯语
    "n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5":
        lambda n: (0 if n == 0 else  # pylint: disable=use-implicit-booleaness-not-comparison-to-zero
                   1 if n == 1 else
                   2 if n == 2 else
                   3 if n % 100 >= 3 and n % 100 <= 10 else
                   4 if n % 100 >= 11 else 5),
}


def _compile_plural_formula(formula: str) -> Callable[[int], int]:
    """Compile a C-style ``Plural-Forms`` formula to a Python callable.

    只支持已知公式表（_PLURAL_FORMULA_TABLE）。未知公式记录 warning 并
    降级为单数形式（lambda _n: 0）——不再使用 eval 动态编译。
    """
    formula = formula.strip()
    fn = _PLURAL_FORMULA_TABLE.get(formula)
    if fn is None:
        logger.warning("Unknown plural formula %r — falling back to singular form", formula)
        return lambda _n: 0
    return fn


# ── Translator class ───────────────────────────────────────────────


class SimplePOTranslator(gettext.NullTranslations):
    """
    .po file translator using Python's standard gettext base class.

    Reads text-format .po files directly and provides the standard gettext API
    (gettext, ngettext, pgettext).  This is a drop-in replacement for the
    hand-rolled parser, now built on CPython's own NullTranslations.

    **Plural forms** are fully supported: the ``Plural-Forms`` header is parsed
    and ``msgid_plural`` / ``msgstr[N]`` entries are loaded into a separate
    catalog.  ``ngettext()`` evaluates the compiled formula at runtime.

    Catalog key scheme (compatible with GNU gettext conventions):

        ``str``            — *msgid* → *msgstr*             (regular)
        ``(str, str)``     — (*msgctxt*, *msgid*) → *msgstr*  (context-aware)

    Plural catalog key scheme:

        ``str``            — *msgid* → (*msgid_plural*, [*msgstr[0]*, …])
    """

    def __init__(self, fp=None):
        self._catalog: Dict[Union[str, tuple], str] = {}
        self._plurals_catalog: Dict[
            Union[str, tuple], Tuple[str, List[str]]
        ] = {}
        self._nplurals: int = 1
        self._plural_fn: Callable[[int], int] = lambda _n: 0
        self.current_locale: str = "en"
        super().__init__(fp)

    # ── .po parsing ────────────────────────────────────────────────

    def _parse(self, fp):
        """Parse a .po file and populate both translation catalogs."""
        content = fp.read() if hasattr(fp, "read") else str(fp)

        # ---- header -------------------------------------------------
        header_match = re.match(
            r'msgid\s+""\s*\nmsgstr\s+""\s*\n((?:"(?:[^"\\]|\\.)*"\s*\n)*)',
            content,
        )
        if header_match:
            self._parse_plural_forms_header(header_match.group(1))
            content = content[header_match.end() :]

        # ---- entry blocks -------------------------------------------
        for block in re.split(r"\n{2,}", content):
            block = block.strip()
            if not block:
                continue
            self._parse_entry(block)

    # ── Header helpers ─────────────────────────────────────────────

    def _parse_plural_forms_header(self, header_continuation: str) -> None:
        """Extract ``Plural-Forms`` from the .po header metadata block."""
        # Concatenate continuation strings
        lines = re.findall(r'"((?:[^"\\]|\\.)*)"', header_continuation)
        full = "".join(
            l.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
            for l in lines
        )

        match = re.search(
            r"Plural-Forms:\s*nplurals\s*=\s*(\d+)\s*;\s*plural\s*=\s*(.+?);",
            full,
        )
        if match:
            self._nplurals = int(match.group(1))
            formula = match.group(2).strip()
            logger.debug("Plural-Forms: nplurals=%d, plural=%s", self._nplurals, formula)
            self._plural_fn = _compile_plural_formula(formula)

    # ── Entry-block helpers ─────────────────────────────────────────

    def _unescape(self, s: str) -> str:
        """Unescape common .po escape sequences."""
        return (
            s.replace("\\n", "\n")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )

    def _parse_entry(self, block: str) -> None:
        """Parse a single .po entry block (one msgid + its msgstr lines)."""
        # Optional context
        ctx_match = re.search(
            r'^msgctxt\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE
        )
        context: Optional[str] = ctx_match.group(1) if ctx_match else None

        # msgid (required)
        id_match = re.search(
            r'^msgid\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE
        )
        if not id_match:
            return
        msgid = self._unescape(id_match.group(1))
        if not msgid:
            return  # header block (already handled)

        key: Union[str, tuple] = (context, msgid) if context else msgid

        # Plural or regular entry?
        plural_match = re.search(
            r'^msgid_plural\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE
        )
        if plural_match:
            # ── plural entry ────────────────────────────────────────
            msgid_plural = self._unescape(plural_match.group(1))
            indices = re.findall(
                r'^msgstr\[(\d+)\]\s+"((?:[^"\\]|\\.)*)"\s*$',
                block,
                re.MULTILINE,
            )
            forms: List[str] = [
                self._unescape(val)
                for _idx_str, val in sorted(indices, key=lambda x: int(x[0]))
            ]
            self._plurals_catalog[key] = (msgid_plural, forms)
        else:
            # ── regular entry ───────────────────────────────────────
            str_match = re.search(
                r'^msgstr\s+"((?:[^"\\]|\\.)*)"\s*$', block, re.MULTILINE
            )
            if str_match:
                self._catalog[key] = self._unescape(str_match.group(1))

    # ── Public load API ────────────────────────────────────────────

    @property
    def translations(self) -> Dict[Union[str, tuple], str]:
        """Backward-compatibility alias for ``_catalog``."""
        return self._catalog

    @translations.setter
    def translations(self, value: Dict[Union[str, tuple], str]) -> None:
        self._catalog = value

    def load_locale(self, locale_code: str, localedir: Path) -> bool:
        """Load translations for *locale_code* from *localedir*."""
        po_file = Path(localedir) / locale_code / "LC_MESSAGES" / "messages.po"
        if not po_file.exists():
            logger.warning("Translation file not found: %s", po_file)
            return False
        self._catalog.clear()
        self._plurals_catalog.clear()
        try:
            with open(po_file, "r", encoding="utf-8") as f:
                self._parse(f)
            self.current_locale = locale_code
            logger.info(
                "Loaded %d translations + %d plural entries for %s",
                len(self._catalog),
                len(self._plurals_catalog),
                locale_code,
            )
            return True
        except (IOError, UnicodeDecodeError) as exc:
            logger.error("Failed to load %s: %s", po_file, exc)
            self._catalog.clear()
            self._plurals_catalog.clear()
            return False

    # ── Standard gettext API ───────────────────────────────────────

    def gettext(self, message: str) -> str:
        """Translate *message*; return *message* itself if untranslated."""
        return self._catalog.get(message, message)

    def pgettext(self, context: str, message: str) -> str:
        """Context-aware translation; return *message* itself if untranslated."""
        try:
            return self._catalog[(context, message)]
        except KeyError:
            return message

    def ngettext(self, msgid1: str, msgid2: str, n: int) -> str:
        """Plural translation using the loaded plural rules.

        If no plural entry is found for *msgid1* the plain fallback
        (singular if ``n == 1`` else plural) is returned.
        """
        entry = self._plurals_catalog.get(msgid1)
        if entry is not None:
            _msgid_plural, forms = entry
            idx = self._plural_fn(n)
            if 0 <= idx < len(forms) and forms[idx] is not None:
                return forms[idx]
            # Fall back to first form if index out of range
            return forms[0] if forms else (msgid1 if n == 1 else msgid2)

        # Also try context-qualified key (singleton tuple to avoid
        # confusion with simple keys)
        # Note: the public ngettext() API does not accept a context,
        # but the catalog may hold context-qualified plural entries.
        return msgid1 if n == 1 else msgid2
