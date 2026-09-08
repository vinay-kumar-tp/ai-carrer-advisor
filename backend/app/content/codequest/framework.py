"""Problem authoring framework for Code Quest.

Design goal: **expected outputs are never written by hand.** A problem declares
its input parameters, a reference solution, and case generators; the build step
runs the reference solution to produce every expected output. A problem whose
reference solution disagrees with its optional independent brute force fails the
build, so a broken problem can never reach the database.

Input convention (identical for every problem, so students learn it once):
stdin is a single whitespace-separated token stream. Every variable-length value
is preceded by its size. Strings never contain whitespace.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional

# ─── Parameter kinds ─────────────────────────────────────────────

INT = "int"
FLOAT = "float"
STR = "str"
INT_LIST = "int[]"
STR_LIST = "str[]"
MATRIX = "int[][]"
GRID = "grid"
PAIR_LIST = "pair[]"
TRIPLE_LIST = "triple[]"
TOKEN_LIST = "token[]"

# ─── Output kinds ────────────────────────────────────────────────

OUT_INT = "int"
OUT_FLOAT = "float"
OUT_STR = "str"
OUT_BOOL = "yesno"
OUT_INT_LIST = "int[]"
OUT_STR_LIST = "str[]"
OUT_MATRIX = "int[][]"
OUT_LINES = "lines"


@dataclass
class Param:
    name: str
    kind: str
    desc: str = ""


DIFFICULTY_POINTS = {"easy": 10, "medium": 25, "hard": 50}
DIFFICULTY_TIME_MS = {"easy": 4000, "medium": 6000, "hard": 8000}


@dataclass
class Spec:
    slug: str
    title: str
    difficulty: str
    topics: list[str]
    patterns: list[str]
    companies: list[str]
    sheets: list[str]
    statement: str
    params: list[Param]
    out_kind: str
    out_desc: str
    solve: Callable[..., Any]
    samples: list[tuple]
    gen: Callable[[random.Random], list[tuple]]
    constraints: list[str]
    hints: list[str]
    notes: list[str] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    pattern_note: str = ""
    brute: Optional[Callable[..., Any]] = None
    points: Optional[int] = None


# ─── stdin serialization ─────────────────────────────────────────

def _tokens_for(kind: str, value: Any) -> list[str]:
    if kind == INT:
        return [str(int(value))]
    if kind == FLOAT:
        return [repr(float(value))]
    if kind == STR:
        text = str(value)
        if text == "":
            raise ValueError("STR values must be non-empty (use a sentinel instead)")
        if any(ch.isspace() for ch in text):
            raise ValueError(f"STR values must not contain whitespace: {text!r}")
        return [text]
    if kind == INT_LIST:
        items = list(value)
        return [str(len(items))] + [str(int(x)) for x in items]
    if kind in (STR_LIST, TOKEN_LIST):
        items = [str(x) for x in value]
        for item in items:
            if item == "" or any(ch.isspace() for ch in item):
                raise ValueError(f"list entries must be non-empty and whitespace-free: {item!r}")
        return [str(len(items))] + items
    if kind == MATRIX:
        rows = [list(r) for r in value]
        cols = len(rows[0]) if rows else 0
        for row in rows:
            if len(row) != cols:
                raise ValueError("matrix rows must all have the same length")
        out = [str(len(rows)), str(cols)]
        for row in rows:
            out.extend(str(int(x)) for x in row)
        return out
    if kind == GRID:
        rows = [str(r) for r in value]
        width = len(rows[0]) if rows else 0
        for row in rows:
            if len(row) != width or any(ch.isspace() for ch in row):
                raise ValueError("grid rows must be equal length and whitespace-free")
        return [str(len(rows)), str(width)] + rows
    if kind == PAIR_LIST:
        pairs = [tuple(p) for p in value]
        out = [str(len(pairs))]
        for pair in pairs:
            if len(pair) != 2:
                raise ValueError("pair[] entries must have exactly 2 values")
            out.extend(str(int(x)) for x in pair)
        return out
    if kind == TRIPLE_LIST:
        triples = [tuple(t) for t in value]
        out = [str(len(triples))]
        for triple in triples:
            if len(triple) != 3:
                raise ValueError("triple[] entries must have exactly 3 values")
            out.extend(str(int(x)) for x in triple)
        return out
    raise ValueError(f"Unknown param kind: {kind}")


def serialize(params: list[Param], args: tuple) -> str:
    """Render an argument tuple as the problem's stdin text."""
    if len(params) != len(args):
        raise ValueError(f"expected {len(params)} args, got {len(args)}")

    lines: list[str] = []
    for param, value in zip(params, args):
        if param.kind in (INT, FLOAT, STR):
            lines.append(_tokens_for(param.kind, value)[0])
        elif param.kind == INT_LIST:
            items = list(value)
            lines.append(str(len(items)))
            lines.append(" ".join(str(int(x)) for x in items))
        elif param.kind in (STR_LIST, TOKEN_LIST):
            items = [str(x) for x in value]
            _tokens_for(param.kind, items)  # validate
            lines.append(str(len(items)))
            lines.extend(items)
        elif param.kind == MATRIX:
            rows = [list(r) for r in value]
            _tokens_for(param.kind, rows)  # validate
            lines.append(f"{len(rows)} {len(rows[0]) if rows else 0}")
            lines.extend(" ".join(str(int(x)) for x in row) for row in rows)
        elif param.kind == GRID:
            rows = [str(r) for r in value]
            _tokens_for(param.kind, rows)  # validate
            lines.append(f"{len(rows)} {len(rows[0]) if rows else 0}")
            lines.extend(rows)
        elif param.kind == PAIR_LIST:
            pairs = [tuple(p) for p in value]
            _tokens_for(param.kind, pairs)  # validate
            lines.append(str(len(pairs)))
            lines.extend(f"{int(a)} {int(b)}" for a, b in pairs)
        elif param.kind == TRIPLE_LIST:
            triples = [tuple(t) for t in value]
            _tokens_for(param.kind, triples)  # validate
            lines.append(str(len(triples)))
            lines.extend(f"{int(a)} {int(b)} {int(c)}" for a, b, c in triples)
        else:
            raise ValueError(f"Unknown param kind: {param.kind}")

    return "\n".join(lines) + "\n"


# ─── Input/output documentation ──────────────────────────────────

def describe_params(params: list[Param]) -> list[str]:
    lines: list[str] = []
    for param in params:
        suffix = f" — {param.desc}" if param.desc else ""
        name = param.name
        if param.kind == INT:
            lines.append(f"A line with the integer `{name}`{suffix}")
        elif param.kind == FLOAT:
            lines.append(f"A line with the real number `{name}`{suffix}")
        elif param.kind == STR:
            lines.append(f"A line with the string `{name}` (no spaces){suffix}")
        elif param.kind == INT_LIST:
            lines.append(f"A line with `n` — the length of `{name}`{suffix}")
            lines.append(f"A line with `n` space-separated integers — the elements of `{name}`")
        elif param.kind in (STR_LIST, TOKEN_LIST):
            lines.append(f"A line with `n` — the number of entries in `{name}`{suffix}")
            lines.append(f"`n` lines, each holding one entry of `{name}`")
        elif param.kind == MATRIX:
            lines.append(f"A line with `r c` — the row and column count of `{name}`{suffix}")
            lines.append(f"`r` lines, each with `c` space-separated integers")
        elif param.kind == GRID:
            lines.append(f"A line with `r c` — the row and column count of `{name}`{suffix}")
            lines.append(f"`r` lines, each a string of exactly `c` characters")
        elif param.kind == PAIR_LIST:
            lines.append(f"A line with `m` — the number of pairs in `{name}`{suffix}")
            lines.append(f"`m` lines, each with 2 space-separated integers")
        elif param.kind == TRIPLE_LIST:
            lines.append(f"A line with `m` — the number of entries in `{name}`{suffix}")
            lines.append(f"`m` lines, each with 3 space-separated integers")
    return lines


def describe_output(kind: str, desc: str) -> list[str]:
    shape = {
        OUT_INT: "Print a single integer.",
        OUT_FLOAT: "Print a single real number rounded to 6 decimal places.",
        OUT_STR: "Print a single line of text.",
        OUT_BOOL: 'Print `YES` or `NO`.',
        OUT_INT_LIST: "Print the integers on one line, separated by single spaces (print an empty line if there are none).",
        OUT_STR_LIST: "Print one entry per line (print nothing if there are none).",
        OUT_MATRIX: "Print each row on its own line, values separated by single spaces.",
        OUT_LINES: "Print one value per line.",
    }[kind]
    return ([desc] if desc else []) + [shape]


# ─── Output formatting ───────────────────────────────────────────

def format_output(kind: str, value: Any) -> str:
    if kind == OUT_INT:
        return str(int(value))
    if kind == OUT_FLOAT:
        return f"{float(value):.6f}"
    if kind == OUT_STR:
        return str(value)
    if kind == OUT_BOOL:
        return "YES" if value else "NO"
    if kind == OUT_INT_LIST:
        return " ".join(str(int(x)) for x in value)
    if kind == OUT_STR_LIST:
        return "\n".join(str(x) for x in value)
    if kind == OUT_MATRIX:
        return "\n".join(" ".join(str(int(x)) for x in row) for row in value)
    if kind == OUT_LINES:
        return "\n".join(str(x) for x in value)
    raise ValueError(f"Unknown output kind: {kind}")


# ─── Starter code ────────────────────────────────────────────────

STARTERS = {
    "python": """import sys

def solution():
    data = sys.stdin.read().split()
    # Parse the input from `data`, then print your answer.
    pass

solution()
""",
    "javascript": """const data = require('fs').readFileSync(0, 'utf8').split(/\\s+/).filter(Boolean);
let ptr = 0;
const next = () => data[ptr++];
const nextInt = () => parseInt(next(), 10);

function solution() {
  // Read values with next() / nextInt(), then console.log your answer.
}

solution();
""",
    "cpp": """#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    // Read the input with cin, then print your answer with cout.
    return 0;
}
""",
    "java": """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        StreamTokenizer in = new StreamTokenizer(new BufferedInputStream(System.in));
        StringBuilder out = new StringBuilder();
        // in.nextToken(); then use (int) in.nval for numbers or in.sval for words.
        System.out.print(out);
    }
}
""",
}


def starter_for(spec: Spec) -> dict[str, str]:
    """Java's StreamTokenizer only suits numeric input; fall back to Scanner otherwise."""
    starters = dict(STARTERS)
    if any(p.kind in (STR, STR_LIST, TOKEN_LIST, GRID) for p in spec.params):
        starters["java"] = """import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer("");
        // Pull whitespace-separated tokens, then print your answer.
        System.out.println();
    }
}
"""
    return starters


# ─── Reference program (used only for verification) ──────────────

PARSE_SNIPPETS = {
    INT: "{name} = int(next(it))",
    FLOAT: "{name} = float(next(it))",
    STR: "{name} = next(it)",
    INT_LIST: "_n = int(next(it)); {name} = [int(next(it)) for _ in range(_n)]",
    STR_LIST: "_n = int(next(it)); {name} = [next(it) for _ in range(_n)]",
    TOKEN_LIST: "_n = int(next(it)); {name} = [next(it) for _ in range(_n)]",
    MATRIX: "_r = int(next(it)); _c = int(next(it)); {name} = [[int(next(it)) for _ in range(_c)] for _ in range(_r)]",
    GRID: "_r = int(next(it)); _c = int(next(it)); {name} = [next(it) for _ in range(_r)]",
    PAIR_LIST: "_m = int(next(it)); {name} = [(int(next(it)), int(next(it))) for _ in range(_m)]",
    TRIPLE_LIST: "_m = int(next(it)); {name} = [(int(next(it)), int(next(it)), int(next(it))) for _ in range(_m)]",
}


def reference_program(spec: Spec) -> str:
    """Build a Python submission that parses stdin per the documented format.

    Deliberately written as an independent parser (a token iterator driven by the
    declared kinds) so it cross-checks the serializer: if the documented format
    were ambiguous or the serializer inconsistent, this program's answers would
    diverge from the stored expected outputs.
    """
    parse_lines = []
    names = []
    for index, param in enumerate(spec.params):
        var = f"a{index}"
        names.append(var)
        parse_lines.append("    " + PARSE_SNIPPETS[param.kind].format(name=var))

    body = "\n".join(parse_lines) if parse_lines else "    pass"
    return f'''import sys
sys.path.insert(0, {chr(39)}{{BACKEND}}{chr(39)})
from app.content.codequest.catalog import get_spec
from app.content.codequest.framework import format_output

def main():
    it = iter(sys.stdin.read().split())
{body}
    spec = get_spec({spec.slug!r})
    result = spec.solve({", ".join(names)})
    sys.stdout.write(format_output({spec.out_kind!r}, result))

main()
'''


# ─── Build ───────────────────────────────────────────────────────

class BuildError(RuntimeError):
    pass


def build(spec: Spec, seed: int = 12345) -> dict:
    """Turn a spec into a database-ready problem, computing every answer."""
    if spec.difficulty not in DIFFICULTY_POINTS:
        raise BuildError(f"{spec.slug}: bad difficulty {spec.difficulty!r}")
    if not spec.samples:
        raise BuildError(f"{spec.slug}: needs at least one sample")
    if not spec.topics or not spec.patterns:
        raise BuildError(f"{spec.slug}: needs topics and patterns")

    rng = random.Random(seed)
    hidden = list(spec.gen(rng))
    if len(hidden) < 4:
        raise BuildError(f"{spec.slug}: needs at least 4 generated cases, got {len(hidden)}")

    def evaluate(args: tuple) -> str:
        try:
            answer = spec.solve(*args)
        except Exception as exc:  # noqa: BLE001 — surfaced as a build failure
            raise BuildError(f"{spec.slug}: reference solution raised on {args!r}: {exc}") from exc
        if spec.brute is not None:
            expected = spec.brute(*args)
            if format_output(spec.out_kind, answer) != format_output(spec.out_kind, expected):
                raise BuildError(
                    f"{spec.slug}: reference disagrees with brute force on {args!r}: "
                    f"{answer!r} vs {expected!r}"
                )
        try:
            return format_output(spec.out_kind, answer)
        except Exception as exc:  # noqa: BLE001
            raise BuildError(f"{spec.slug}: cannot format {answer!r}: {exc}") from exc

    examples = []
    test_cases = []

    for index, args in enumerate(spec.samples):
        stdin_text = serialize(spec.params, args)
        expected = evaluate(args)
        explanation = spec.explanations[index] if index < len(spec.explanations) else ""
        examples.append({"input": stdin_text.rstrip("\n"), "output": expected, "explanation": explanation})
        test_cases.append({"input": stdin_text, "expected_output": expected, "is_sample": True})

    for args in hidden:
        stdin_text = serialize(spec.params, args)
        test_cases.append({"input": stdin_text, "expected_output": evaluate(args), "is_sample": False})

    points = spec.points or DIFFICULTY_POINTS[spec.difficulty]

    return {
        "slug": spec.slug,
        "title": spec.title,
        "difficulty": spec.difficulty,
        "description": spec.statement.strip(),
        "notes": list(spec.notes),
        "topics": list(spec.topics),
        "patterns": list(spec.patterns),
        "companies": list(spec.companies),
        "sheets": list(spec.sheets),
        "tags": list(spec.topics),
        "input_format": describe_params(spec.params),
        "output_format": describe_output(spec.out_kind, spec.out_desc),
        "constraints": list(spec.constraints),
        "examples": examples,
        "hints": list(spec.hints),
        "pattern_note": spec.pattern_note,
        "test_cases": test_cases,
        "sample_input": examples[0]["input"],
        "sample_output": examples[0]["output"],
        "starter_code": starter_for(spec),
        "languages": ["python", "javascript", "cpp", "java"],
        "points": points,
        "xp_reward": points,
        "time_limit_ms": DIFFICULTY_TIME_MS[spec.difficulty],
    }


# ─── Authoring helpers ───────────────────────────────────────────

LOWER = "abcdefghijklmnopqrstuvwxyz"


def ints(rng: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return [rng.randint(lo, hi) for _ in range(n)]


def word(rng: random.Random, n: int, alphabet: str = LOWER) -> str:
    return "".join(rng.choice(alphabet) for _ in range(n))


def words(rng: random.Random, count: int, lo: int, hi: int, alphabet: str = LOWER) -> list[str]:
    return [word(rng, rng.randint(lo, hi), alphabet) for _ in range(count)]


def sorted_ints(rng: random.Random, n: int, lo: int, hi: int) -> list[int]:
    return sorted(ints(rng, n, lo, hi))


def matrix(rng: random.Random, r: int, c: int, lo: int, hi: int) -> list[list[int]]:
    return [ints(rng, c, lo, hi) for _ in range(r)]


def grid(rng: random.Random, r: int, c: int, alphabet: str) -> list[str]:
    return [word(rng, c, alphabet) for _ in range(r)]


def tree_tokens(rng: random.Random, size: int, lo: int = 1, hi: int = 99) -> list[str]:
    """Level-order tokens for a random binary tree; `null` marks a missing child.

    Always returns a valid level-order encoding: a `null` never has children.
    """
    if size <= 0:
        return ["null"]
    tokens = [str(rng.randint(lo, hi))]
    slots = 2  # children of the root
    placed = 1
    index = 0
    while index < len(tokens) and placed < size:
        if tokens[index] == "null":
            index += 1
            continue
        for _ in range(2):
            if placed < size and rng.random() < 0.75:
                tokens.append(str(rng.randint(lo, hi)))
                placed += 1
            else:
                tokens.append("null")
        index += 1
    # Trim trailing nulls for a tidy encoding.
    while len(tokens) > 1 and tokens[-1] == "null":
        tokens.pop()
    return tokens


class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int):
        self.val = val
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None


def build_tree(tokens: Iterable[str]) -> Optional[TreeNode]:
    """Decode level-order tokens (with `null`) into a binary tree."""
    items = list(tokens)
    if not items or items[0] == "null":
        return None
    root = TreeNode(int(items[0]))
    queue = [root]
    head = 0
    index = 1
    while head < len(queue) and index < len(items):
        node = queue[head]
        head += 1
        if index < len(items):
            token = items[index]
            index += 1
            if token != "null":
                node.left = TreeNode(int(token))
                queue.append(node.left)
        if index < len(items):
            token = items[index]
            index += 1
            if token != "null":
                node.right = TreeNode(int(token))
                queue.append(node.right)
    return root


def bst_tokens(values: list[int]) -> list[str]:
    """Level-order encoding of a BST built by inserting `values` in order."""
    root: Optional[TreeNode] = None

    def insert(node: Optional[TreeNode], value: int) -> TreeNode:
        if node is None:
            return TreeNode(value)
        if value < node.val:
            node.left = insert(node.left, value)
        elif value > node.val:
            node.right = insert(node.right, value)
        return node

    for value in values:
        root = insert(root, value)

    if root is None:
        return ["null"]

    tokens: list[str] = []
    queue: list[Optional[TreeNode]] = [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            tokens.append("null")
            continue
        tokens.append(str(node.val))
        queue.append(node.left)
        queue.append(node.right)
    while len(tokens) > 1 and tokens[-1] == "null":
        tokens.pop()
    return tokens


def connected_edges(rng: random.Random, n: int, extra: int = 0) -> list[tuple[int, int]]:
    """A random spanning tree on 1..n plus `extra` additional distinct edges."""
    edges: set[tuple[int, int]] = set()
    for node in range(2, n + 1):
        parent = rng.randint(1, node - 1)
        edges.add((min(parent, node), max(parent, node)))
    attempts = 0
    while extra > 0 and attempts < extra * 20:
        attempts += 1
        u = rng.randint(1, n)
        v = rng.randint(1, n)
        if u == v:
            continue
        edge = (min(u, v), max(u, v))
        if edge not in edges:
            edges.add(edge)
            extra -= 1
    return sorted(edges)


def dag_edges(rng: random.Random, n: int, density: float = 0.25) -> list[tuple[int, int]]:
    """Random DAG on 1..n — edges always run from a lower to a higher label."""
    order = list(range(1, n + 1))
    rng.shuffle(order)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < density:
                edges.append((order[i], order[j]))
    return edges


# ─── Compact spec constructor ────────────────────────────────────

def P(
    slug: str,
    title: str,
    difficulty: str,
    topics: list[str],
    patterns: list[str],
    statement: str,
    params: list[Param],
    out_kind: str,
    solve: Callable[..., Any],
    samples: list[tuple],
    gen: Callable[[random.Random], list[tuple]],
    constraints: list[str],
    hints: list[str],
    notes: Iterable[str] = (),
    explanations: Iterable[str] = (),
    out_desc: str = "",
    brute: Optional[Callable[..., Any]] = None,
    companies: Optional[list[str]] = None,
    sheets: Optional[list[str]] = None,
    pattern_note: str = "",
    points: Optional[int] = None,
) -> Spec:
    """Build a Spec, auto-tagging companies/sheets when not given explicitly."""
    from app.content.codequest.tagging import auto_companies, auto_sheets

    return Spec(
        slug=slug,
        title=title,
        difficulty=difficulty,
        topics=topics,
        patterns=patterns,
        companies=companies if companies is not None else auto_companies(slug, difficulty, topics),
        sheets=sheets if sheets is not None else auto_sheets(slug, difficulty),
        statement=statement,
        params=params,
        out_kind=out_kind,
        out_desc=out_desc,
        solve=solve,
        samples=samples,
        gen=gen,
        constraints=constraints,
        hints=hints,
        notes=list(notes),
        explanations=list(explanations),
        pattern_note=pattern_note,
        brute=brute,
        points=points,
    )


# Frequently reused parameter shapes.
def p_nums(desc: str = "the array") -> Param:
    return Param("nums", INT_LIST, desc)


def p_int(name: str, desc: str = "") -> Param:
    return Param(name, INT, desc)


def p_str(name: str = "s", desc: str = "") -> Param:
    return Param(name, STR, desc)
