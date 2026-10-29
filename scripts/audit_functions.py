"""Inventory production functions and flag clone candidates; never rewrite source.

Run: python scripts/audit_functions.py
Outputs: docs/function-audit/inventory.csv and candidates.json.
Similarity is a screening hint, not proof that two functions are interchangeable.
"""

import argparse
import ast
import csv
import io
import json
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path


class FunctionCollector(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.scope = []
        self.functions = []

    def visit_ClassDef(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node):
        name = ".".join([*self.scope, node.name])
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str):
                body = body[1:]
        module = ast.Module(body=body, type_ignores=[])
        calls = sorted({ast.unparse(n.func) for n in ast.walk(module) if isinstance(n, ast.Call)})
        self.functions.append({
            "file": self.path,
            "name": name,
            "line": node.lineno,
            "end_line": node.end_lineno,
            "calls": calls,
            "_body": ast.dump(module, include_attributes=False),
            "_statements": sum(isinstance(n, ast.stmt) for n in ast.walk(module)),
        })
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef


def collect_functions(root):
    functions = []
    for path in sorted((root / "src").rglob("*.py")):
        collector = FunctionCollector(path.relative_to(root).as_posix())
        collector.visit(ast.parse(path.read_text(encoding="utf-8-sig")))
        functions.extend(collector.functions)
    return functions


def find_candidates(functions):
    # Tiny wrappers, getters and abstract stubs are deliberately not clone candidates.
    eligible = [f for f in functions if f["_statements"] >= 4]
    bodies = defaultdict(list)
    names = defaultdict(list)
    calls = defaultdict(list)
    for i, function in enumerate(eligible):
        bodies[function["_body"]].append(i)
        names[function["name"].split(".")[-1]].append(i)
        for call in function["calls"]:
            calls[call].append(i)

    def location(index):
        f = eligible[index]
        return {key: f[key] for key in ("file", "name", "line")}

    exact = [[location(i) for i in group] for group in bodies.values() if len(group) > 1]
    pairs = set()
    for i, function in enumerate(eligible):
        shared = defaultdict(int)
        for call in function["calls"]:
            for j in calls[call]:
                if j > i:
                    shared[j] += 1
        peers = {j for j in names[function["name"].split(".")[-1]] if j > i}
        peers.update(j for j, count in shared.items() if count >= 2)
        pairs.update((i, j) for j in peers)
    similar = []
    for i, j in sorted(pairs):
        left, right = eligible[i], eligible[j]
        if left["file"] == right["file"] and left["line"] <= right["line"] <= left["end_line"]:
            continue  # A closure is part of its enclosing function, not a second implementation.
        a, b = left["_body"], right["_body"]
        if a == b:
            continue
        matcher = SequenceMatcher(None, a, b)
        if matcher.quick_ratio() < 0.9:
            continue
        ratio = matcher.ratio()
        if ratio >= 0.9:
            similar.append({"similarity": round(ratio, 3), "functions": [location(i), location(j)]})
    return {"exact_body_groups": exact, "similar_pairs": similar}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    functions = collect_functions(args.root)
    candidates = find_candidates(functions)
    output = args.root / "docs" / "function-audit"
    output.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(["file", "qualified_name", "line", "end_line", "calls_unresolved"])
    for function in functions:
        writer.writerow([function["file"], function["name"], function["line"],
                         function["end_line"], "; ".join(function["calls"])])
    (output / "inventory.csv").write_text(buffer.getvalue(), encoding="utf-8")
    report = {
        "python_files": len(list((args.root / "src").rglob("*.py"))),
        "files": len({f["file"] for f in functions}),
        "functions": len(functions),
        "limitations": "Calls are syntax-only, not resolved references. Candidates require manual review; dynamic Qt signals and semantic clones may be missed.",
        **candidates,
    }
    (output / "candidates.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{report['files']} files with functions, {len(functions)} functions; "
          f"{len(candidates['exact_body_groups'])} exact groups, "
          f"{len(candidates['similar_pairs'])} similar pairs. Output: {output}")


if __name__ == "__main__":
    main()
