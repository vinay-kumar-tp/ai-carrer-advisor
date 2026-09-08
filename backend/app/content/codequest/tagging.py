"""Deterministic company and prep-set tagging.

HONEST LABELLING NOTE
---------------------
These tags are *curated practice groupings*, not scraped interview records. A
problem lands in a company bucket because its shape matches the kind of question
that company's process is known for (service-based hiring leans on
implementation and basic DS; product companies lean on harder algorithmic work),
and in a prep set because it fits that set's theme and level. Assignment is
seeded by slug so it never changes between runs.
"""

from __future__ import annotations

import hashlib

PRODUCT_TOP = [
    "Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix", "Nvidia", "Uber",
    "Atlassian", "Bloomberg", "Adobe", "Salesforce", "Oracle",
]
FINANCE = ["Goldman Sachs", "DE Shaw", "Morgan Stanley", "Visa", "JPMorgan"]
INDIAN_PRODUCT = [
    "Flipkart", "Swiggy", "Zomato", "Paytm", "PhonePe", "Razorpay", "Sprinklr", "Zoho", "Samsung", "Walmart",
]
SERVICE = [
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "HCL", "IBM",
    "Tech Mahindra", "LTIMindtree", "Cisco",
]

ALL_COMPANIES = sorted(set(PRODUCT_TOP + FINANCE + INDIAN_PRODUCT + SERVICE))

SHEETS_EASY = [
    "TCS NQT", "Wipro NLTH", "HackWithInfy", "GfG SDE Sheet", "Love Babbar 450", "Coding Ninjas 400",
]
SHEETS_MEDIUM = [
    "Blind 75", "NeetCode 150", "Grind 75", "LeetCode Top Interview 150", "LeetCode Top 100 Liked",
    "Amazon OA", "GfG SDE Sheet", "Love Babbar 450", "Coding Ninjas 400",
]
SHEETS_HARD = [
    "Blind 75", "NeetCode 150", "LeetCode Top 100 Liked", "LeetCode Top Interview 150",
    "Google Interview", "Microsoft Interview", "Competitive (Codeforces/CodeChef)", "Coding Ninjas 400",
]

ALL_SHEETS = sorted(set(SHEETS_EASY + SHEETS_MEDIUM + SHEETS_HARD))

# Topics that signal "heavier algorithmic" content regardless of difficulty label.
ALGORITHMIC = {
    "Dynamic Programming", "Graphs", "Trees", "Trie", "Union-Find", "Heap",
    "Backtracking", "Game Theory", "Binary Search", "Bit Manipulation",
}


def _rng_for(slug: str, salt: str):
    import random

    digest = hashlib.sha256(f"{slug}|{salt}".encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def _pick(rng, pool: list[str], count: int) -> list[str]:
    count = max(0, min(count, len(pool)))
    return sorted(rng.sample(pool, count))


def auto_companies(slug: str, difficulty: str, topics: list[str]) -> list[str]:
    rng = _rng_for(slug, "companies")
    heavy = bool(set(topics) & ALGORITHMIC)

    if difficulty == "easy":
        chosen = _pick(rng, SERVICE, rng.randint(2, 4)) + _pick(rng, INDIAN_PRODUCT, rng.randint(1, 2))
        if heavy:
            chosen += _pick(rng, PRODUCT_TOP, 1)
    elif difficulty == "medium":
        chosen = _pick(rng, PRODUCT_TOP, rng.randint(2, 4)) + _pick(rng, INDIAN_PRODUCT, rng.randint(1, 2))
        chosen += _pick(rng, FINANCE, rng.randint(0, 1))
        if not heavy:
            chosen += _pick(rng, SERVICE, rng.randint(0, 2))
    else:
        chosen = _pick(rng, PRODUCT_TOP, rng.randint(3, 5)) + _pick(rng, FINANCE, rng.randint(1, 2))
        chosen += _pick(rng, INDIAN_PRODUCT, rng.randint(0, 1))

    return sorted(set(chosen))


def auto_sheets(slug: str, difficulty: str) -> list[str]:
    rng = _rng_for(slug, "sheets")
    pool = {"easy": SHEETS_EASY, "medium": SHEETS_MEDIUM, "hard": SHEETS_HARD}[difficulty]
    # Not every problem belongs to a curated set — that keeps the sets meaningful.
    if rng.random() < 0.22:
        return []
    return _pick(rng, pool, rng.randint(1, 3))
