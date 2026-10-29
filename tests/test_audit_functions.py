"""The inventory is deterministic and candidates are hints, not automated rewrites."""

import csv
import json

from scripts.audit_functions import collect_functions, find_candidates, main

SOURCE = '''
class Example:
    async def outer(self):
        def nested(value):
            result = transform(value)
            result = validate(result)
            log(result)
            return result
        result = transform(1)
        result = validate(result)
        log(result)
        return nested(result)

def first(value):
    """Documentation is not an implementation difference."""
    result = transform(value)
    result = validate(result)
    log(result)
    return result

def second(value):
    result = transform(value)
    result = validate(result)
    log(result)
    return result

def short():
    return True
'''


def test_inventory_includes_scopes_async_and_calls(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "example.py").write_text(SOURCE, encoding="utf-8")
    functions = collect_functions(tmp_path)
    assert [f["name"] for f in functions] == [
        "Example.outer", "Example.outer.nested", "first", "second", "short"
    ]
    assert functions[2]["calls"] == ["log", "transform", "validate"]
    candidates = find_candidates(functions)
    assert len(candidates["exact_body_groups"]) == 1
    assert {f["name"] for f in candidates["exact_body_groups"][0]} == {
        "Example.outer.nested", "first", "second"
    }
    for pair in candidates["similar_pairs"]:
        assert {f["name"] for f in pair["functions"]} != {
            "Example.outer", "Example.outer.nested"
        }


def test_cli_writes_portable_inventory_without_modifying_source(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    path = src / "example.py"
    path.write_text(SOURCE, encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["audit_functions.py", "--root", str(tmp_path)])
    main()
    output = tmp_path / "docs/function-audit"
    with (output / "inventory.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 5
    assert rows[0]["file"] == "src/example.py"
    report = json.loads((output / "candidates.json").read_text(encoding="utf-8"))
    assert report["functions"] == 5
    assert report["python_files"] == 1
    assert path.read_text(encoding="utf-8") == SOURCE
