# Internationalization (i18n) Guide

This document describes how to use the internationalization framework in the Battery Analysis application.

## Quick Start

The application uses GNU gettext for internationalization. All translatable strings should use the `_()` function.

### In Python Code

```python
from battery_analysis.i18n import _

# Simple translation
label.setText(_("File"))

# Context-aware translation (for ambiguous terms)
status = pgettext("file_status", "Open")

# Plural forms
message = ngettext("One file processed", "%d files processed", count)
```

## Working with Translations

### Adding New Translatable Strings

1. Wrap strings with `_()` in your code
2. Extract strings: `python scripts/extract_translations.py`
3. Edit translation files in `locale/{locale}/LC_MESSAGES/messages.po`
4. Compile: `python scripts/compile_translations.py`

### Adding a New Language

1. Create directory: `locale/{locale_code}/LC_MESSAGES/`
2. Copy `messages.po` from an existing language
3. Translate the strings
4. Compile translations
5. Add to `SUPPORTED_LOCALES` in `language_manager.py`

## Directory Structure

```
locale/
├── en/LC_MESSAGES/
│   ├── messages.po    # English translations
│   └── messages.mo    # Compiled
├── zh_CN/LC_MESSAGES/
│   ├── messages.po    # Chinese translations
│   └── messages.mo    # Compiled
└── messages.pot       # Translation template
```

## Available Scripts

- `compile_translations.py` - Compile .po to .mo files
- `extract_translations.py` - Extract translatable strings from code
- `setup_i18n.py` - Initialize i18n framework
