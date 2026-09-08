"""Registry that stitches the themed problem modules together."""

from __future__ import annotations

import importlib
from functools import lru_cache

from app.content.codequest.framework import Spec, build

MODULES = [
    "arrays",
    "strings",
    "math_nt",
    "hashing",
    "two_pointers",
    "sliding_window",
    "prefix_sum",
    "sorting_searching",
    "binary_search",
    "bits",
    "matrix",
    "stack_queue",
    "linked_list",
    "trees",
    "graphs",
    "dp",
    "greedy",
    "intervals",
    "heap_topk",
    "trie",
    "union_find",
    "backtracking",
    "game_theory",
]


@lru_cache(maxsize=1)
def iter_specs() -> tuple[Spec, ...]:
    specs: list[Spec] = []
    seen: dict[str, str] = {}

    for name in MODULES:
        module = importlib.import_module(f"app.content.codequest.{name}")
        for spec in module.specs():
            if spec.slug in seen:
                raise ValueError(f"duplicate slug {spec.slug!r} in {name} (already in {seen[spec.slug]})")
            seen[spec.slug] = name
            specs.append(spec)

    return tuple(specs)


@lru_cache(maxsize=1)
def _by_slug() -> dict[str, Spec]:
    return {spec.slug: spec for spec in iter_specs()}


def get_spec(slug: str) -> Spec:
    try:
        return _by_slug()[slug]
    except KeyError as exc:
        raise KeyError(f"Unknown problem slug: {slug}") from exc


def spec_count() -> int:
    return len(iter_specs())


def build_all(seed: int = 12345) -> list[dict]:
    """Build every problem, computing all expected outputs. Raises on any error."""
    out = []
    for index, spec in enumerate(iter_specs()):
        problem = build(spec, seed=seed + index)
        problem["display_order"] = index
        out.append(problem)
    return out
