"""Authoring primitives for Big Five (OCEAN) assessment forms.

Each form is an ordered list of :class:`Item`. An item belongs to exactly one of
the five OCEAN traits and is either positively or negatively keyed:

* Positive keying:  score = response
* Negative keying:  score = 6 - response   (reverse scored)

The 1–5 Likert scale is fixed (1 = Disagree strongly … 5 = Agree strongly), so a
trait's raw score ranges from ``n items`` (all 1s after keying) to ``5 * n``.
The scale minimum/maximum used for percentage conversion is derived per trait.
"""

from __future__ import annotations

from dataclasses import dataclass

# Canonical OCEAN traits.
TRAITS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

TRAIT_LABELS = {
    "openness": "Openness to Experience",
    "conscientiousness": "Conscientiousness",
    "extraversion": "Extraversion",
    "agreeableness": "Agreeableness",
    "neuroticism": "Neuroticism",
}

# 1..5 Likert scale (shared by every item).
SCALE = [
    {"value": 1, "label": "Disagree strongly"},
    {"value": 2, "label": "Disagree a little"},
    {"value": 3, "label": "Neither agree nor disagree"},
    {"value": 4, "label": "Agree a little"},
    {"value": 5, "label": "Agree strongly"},
]
SCALE_MIN = 1
SCALE_MAX = 5


@dataclass(frozen=True)
class Item:
    text: str
    trait: str
    keyed: str = "+"          # "+" positive, "-" negative (reverse scored)
    facet: str = ""           # optional facet name (IPIP-NEO uses 6 facets/trait)

    def __post_init__(self):
        if self.trait not in TRAITS:
            raise ValueError(f"bad trait {self.trait!r} for item: {self.text[:40]!r}")
        if self.keyed not in ("+", "-"):
            raise ValueError(f"keyed must be '+' or '-' for item: {self.text[:40]!r}")

    def score(self, response: int) -> int:
        """Apply directionality to a 1–5 response."""
        if not (SCALE_MIN <= response <= SCALE_MAX):
            raise ValueError(f"response {response} out of 1..5 range")
        return response if self.keyed == "+" else (SCALE_MIN + SCALE_MAX - response)


def I(text: str, trait: str, keyed: str = "+", facet: str = "") -> Item:  # noqa: E743
    return Item(text=text, trait=trait, keyed=keyed, facet=facet)


@dataclass(frozen=True)
class Form:
    key: str                  # "bfi44" | "ipip120"
    name: str
    short_name: str
    description: str
    est_minutes: int
    items: list[Item]

    @property
    def total_questions(self) -> int:
        return len(self.items)

    def trait_bounds(self) -> dict[str, dict]:
        """Per-trait item count and the min/max raw score used for %."""
        counts: dict[str, int] = {t: 0 for t in TRAITS}
        for item in self.items:
            counts[item.trait] += 1
        return {
            t: {
                "items": counts[t],
                "min_score": counts[t] * SCALE_MIN,
                "max_score": counts[t] * SCALE_MAX,
            }
            for t in TRAITS
        }
