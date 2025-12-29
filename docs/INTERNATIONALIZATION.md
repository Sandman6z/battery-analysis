# Internationalization (i18n) Guide

This document describes the internationalization framework for the Battery Analysis application.

## Overview

The application uses standard GNU gettext-based internationalization following Python best practices.

## Directory Structure

```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── messages.po    # English translations (source)
│       └── messages.mo    # English translations (compiled)
├── zh_CN/
│   └── LC_MESSAGES/
│       ├── messages.po    # Chinese translations (source)
│       └── messages.mo    # Chinese translations (compiled)
└── messages.pot           # Translation template
```

## Usage

### In Python Code

```python
from battery_analysis.i18n import _

# Simple translation
label.setText(_("File"))

# Context-aware translation
status = pgettext("file_status", "Open")

# Plural forms
message = ngettext("One file processed", "%d files processed", count)
```

### Translation Files

#### Adding New Translations

1. Edit `.po` files in `locale/{locale}/LC_MESSAGES/`
2. Compile using: `python scripts/compile_translations_python.py`
3. Test with: `python scripts/test_i18n.py`

#### Extracting New Strings

1. Add `_("string")` calls in Python code
2. Extract using: `python scripts/extract_translations.py`
3. Update `.po` files with new strings
4. Recompile translations

## Scripts

- `compile_translations_python.py`: Compile .po to .mo files
- `extract_translations.py`: Extract translatable strings from code
- `setup_i18n.py`: Setup i18n framework
- `test_i18n.py`: Test i18n functionality

## Standards Compliance

This implementation follows:
- GNU gettext standards
- Python i18n best practices
- Qt translation conventions
- POSIX locale standards

## Adding New Languages

1. Create directory: `locale/{locale_code}/LC_MESSAGES/`
2. Copy `messages.po` from existing language
3. Update translations
4. Compile with `compile_translations_python.py`
5. Add to `SUPPORTED_LOCALES` in `language_manager.py`
