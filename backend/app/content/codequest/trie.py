"""Trie / prefix tree problems."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR,
    P,
    Param,
    STR,
    STR_LIST,
    p_int,
    word,
    words,
)

T = ["Trie"]
TR = ["Trie"]
TP = ["Trie / Prefix Search"]
SMALL = "abc"


def p_words(name="wordsList", desc="the dictionary words"):
    return Param(name, STR_LIST, desc)


def g_words(counts=(1, 2, 4, 9, 25, 70, 180)):
    def gen(rng: random.Random):
        return [(words(rng, count, 1, 5, SMALL),) for count in counts]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "trie-contains-word", "Trie Word Lookup", "medium", T + ["Strings"], TR,
        "Insert every word of `wordsList` into a trie, then print `YES` if `query` is present as a complete "
        "word, else `NO`.",
        [p_words(), Param("query", STR, "the word to look up")], OUT_BOOL,
        lambda wordsList, query: query in set(wordsList),
        [(["apple", "app"], "app"), (["apple"], "ap")],
        lambda rng: [(lambda ws: (ws, rng.choice(ws) if rng.random() < 0.6 else word(rng, rng.randint(1, 4), SMALL)))(
            words(rng, count, 1, 5, SMALL)) for count in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100", "lowercase English letters only"],
        ["Each trie node holds up to 26 child pointers plus an end-of-word flag.",
         "Walk the query character by character; a missing child means the word is absent.",
         "The end-of-word flag distinguishes a stored word from a mere prefix.",
         "Lookup costs O(|query|), independent of how many words are stored."],
        explanations=["app was inserted as a complete word.", "ap is only a prefix."],
    ))

    add(P(
        "trie-starts-with-prefix", "Trie Prefix Lookup", "medium", T + ["Strings"], TP,
        "Print `YES` if any word of `wordsList` starts with `prefix`, else `NO`.",
        [p_words(), Param("prefix", STR, "the prefix to test")], OUT_BOOL,
        lambda wordsList, prefix: any(w.startswith(prefix) for w in wordsList),
        [(["apple", "banana"], "app"), (["apple"], "b")],
        lambda rng: [(lambda ws: (ws, word(rng, rng.randint(1, 3), SMALL)))(
            words(rng, count, 1, 5, SMALL)) for count in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100"],
        ["Walk the prefix down the trie without checking any end-of-word flag.",
         "Reaching the last character successfully means at least one word extends it.",
         "This is the operation a trie does far better than a plain list."],
        explanations=["apple starts with app.", "No word starts with b."],
    ))

    add(P(
        "count-words-with-prefix", "Count Words With Prefix", "medium", T + ["Strings"], TP,
        "Print how many words of `wordsList` start with `prefix`.",
        [p_words(), Param("prefix", STR, "the prefix to count")], OUT_INT,
        lambda wordsList, prefix: sum(1 for w in wordsList if w.startswith(prefix)),
        [(["app", "apple", "banana"], "app"), (["cat"], "d")],
        lambda rng: [(lambda ws: (ws, word(rng, rng.randint(1, 3), SMALL)))(
            words(rng, count, 1, 5, SMALL)) for count in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100"],
        ["Store a counter on every trie node recording how many inserted words pass through it.",
         "Walking to the prefix's final node then answers in O(|prefix|).",
         "Without that counter you would have to enumerate the whole subtree."],
        explanations=["app and apple qualify.", "No word starts with d."],
    ))

    add(P(
        "longest-common-prefix-trie", "Longest Common Prefix Via Trie", "medium", T + ["Strings"], TP,
        "Print the longest prefix shared by every word of `wordsList`. Print an empty line if there is none.",
        [p_words()], OUT_STR, lambda wordsList: _lcp(wordsList),
        [(["flower", "flow", "flight"],), (["dog", "cat"],)],
        lambda rng: [(_prefix_family(rng, count),) for count in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100"],
        ["Insert everything, then walk down from the root while each node has exactly one child and is "
         "not an end-of-word.",
         "The path you walk spells the longest common prefix.",
         "Comparing the words column by column is simpler and equally correct."],
        explanations=["fl is shared by all three.", "They share nothing."],
    ))

    add(P(
        "count-distinct-substrings-trie", "Count Distinct Substrings", "hard", T + ["Strings"], TR,
        "Print how many distinct non-empty substrings the string `s` has.",
        [Param("s", STR, "lowercase letters")], OUT_INT,
        lambda s: len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)}),
        [("ababa",), ("aaa",)],
        lambda rng: [(word(rng, n, "ab"),) for n in (1, 2, 3, 5, 9, 16, 30, 60)],
        ["1 <= |s| <= 200", "s contains lowercase English letters only"],
        ["Insert every suffix into a trie; each distinct node below the root is one distinct substring.",
         "That counts each substring exactly once because the trie merges shared prefixes.",
         "A suffix automaton or suffix array does this in linear time.",
         "Collecting substrings in a hash set is simplest at these limits."],
        explanations=["a,b,ab,ba,aba,bab,abab,baba,ababa gives 9.", "a, aa and aaa give 3."],
    ))

    add(P(
        "shortest-unique-prefixes", "Shortest Unique Prefixes", "medium", T + ["Strings"], TP,
        "For each word of `wordsList` (all distinct), print the length of its shortest prefix that no other "
        "word shares. Print the lengths in the input order, space separated.",
        [Param("wordsList", STR_LIST, "distinct words")], OUT_INT_LIST,
        lambda wordsList: _unique_prefix_lengths(wordsList),
        [(["dog", "dove", "duck", "zebra"],), (["cat"],)],
        lambda rng: [(_distinct_words(rng, count),) for count in (1, 2, 4, 9, 25, 70)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100", "all words are distinct"],
        ["Store a pass-through count on every trie node.",
         "Walk each word until you find a node with a count of 1 — that prefix is unique.",
         "If no such node exists, the whole word is the answer (it is a prefix of another word)."],
        explanations=["do is ambiguous, so dog needs 3; dove needs 3; du needs 2; z needs 1.",
                      "One word needs a single character."],
        brute=lambda wordsList: _unique_prefix_brute(wordsList),
    ))

    add(P(
        "wildcard-single-char-match", "Match With Single Wildcards", "medium", T + ["Strings"], TR,
        "The `pattern` may contain `.` characters, each matching exactly one letter. Print how many words "
        "of `wordsList` the pattern matches (lengths must be equal).",
        [p_words(), Param("pattern", STR, "letters and . wildcards")], OUT_INT,
        lambda wordsList, pattern: sum(1 for w in wordsList if _matches(w, pattern)),
        [(["cat", "cot", "dog"], "c.t"), (["cat"], "ca")],
        lambda rng: [(lambda ws: (ws, "".join(rng.choice("abc.") for _ in range(rng.randint(1, 4)))))(
            words(rng, count, 1, 4, SMALL)) for count in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= number of words <= 1000", "1 <= |pattern| <= 100",
         "pattern contains lowercase letters and . only"],
        ["Walk the trie one pattern character at a time.",
         "A literal follows one child; a `.` branches into every existing child.",
         "That branching search is what a plain hash set cannot do.",
         "Words of a different length can never match."],
        explanations=["cat and cot match c.t.", "The lengths differ."],
    ))

    add(P(
        "max-xor-pair-trie", "Maximum XOR Of Two Numbers", "hard", T + ["Bit Manipulation", "Arrays"], TR,
        "Print the largest XOR obtainable from two elements of `nums` at different positions.",
        [Param("nums", "int[]", "at least 2 non-negative integers")], OUT_INT,
        lambda nums: _max_xor(nums),
        [([3, 10, 5, 25, 2, 8],), ([1, 1],)],
        lambda rng: [([rng.randint(0, 5000) for _ in range(n)],) for n in (2, 3, 5, 9, 20, 55, 140, 300)],
        ["2 <= n <= 2000", "0 <= nums[i] <= 10^6"],
        ["Insert the numbers into a binary trie, most significant bit first.",
         "For each number, walk the trie preferring the opposite bit at every level to maximise the XOR.",
         "That gives O(n * bits) instead of the O(n^2) pair loop.",
         "The greedy choice is safe because a higher bit outweighs everything below it."],
        explanations=["5 XOR 25 = 28.", "1 XOR 1 = 0."],
        brute=lambda nums: max(nums[i] ^ nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums))),
    ))

    add(P(
        "count-prefix-pairs", "Count Prefix Pairs", "medium", T + ["Strings"], TP,
        "Count the ordered pairs `(i, j)` with `i != j` where `wordsList[i]` is a prefix of `wordsList[j]`.",
        [p_words()], OUT_INT, lambda wordsList: _count_prefix_pairs(wordsList),
        [(["a", "ab", "abc"],), (["x", "y"],)],
        g_words(),
        ["1 <= number of words <= 1000", "1 <= |word| <= 100",
         "the answer fits in a 64-bit signed integer"],
        ["Insert every word, then for each word walk its path counting end-of-word markers along the way.",
         "Each marker you pass is a shorter word that prefixes this one.",
         "Exclude the word's own marker at the end of its path.",
         "The double loop with startsWith is O(n^2 * |word|) and passes here."],
        explanations=["(a,ab), (a,abc) and (ab,abc) give 3.", "Neither prefixes the other."],
        brute=lambda wordsList: sum(
            1 for i in range(len(wordsList)) for j in range(len(wordsList))
            if i != j and wordsList[j].startswith(wordsList[i])
        ),
    ))

    add(P(
        "replace-words-with-roots", "Replace Words With Roots", "medium", T + ["Strings"], TP,
        "For each word of `wordsList`, replace it with the shortest word of `roots` that is a prefix of it, "
        "or leave it unchanged when no root applies. Print the results one per line.",
        [Param("roots", STR_LIST, "the root words"), p_words("wordsList", "the sentence words")],
        "str[]", lambda roots, wordsList: _replace_with_roots(roots, wordsList),
        [(["cat", "bat"], ["cattle", "batman", "dog"]), (["a"], ["b"])],
        lambda rng: [(words(rng, rng.randint(1, 4), 1, 3, SMALL), words(rng, count, 1, 5, SMALL))
                     for count in (1, 2, 4, 9, 25, 70)],
        ["1 <= number of roots, words <= 1000", "1 <= |word| <= 100"],
        ["Insert the roots into a trie.",
         "Walk each word and stop at the first end-of-word marker you reach — that is the shortest root.",
         "If you fall off the trie, keep the original word."],
        explanations=["cattle -> cat, batman -> bat, dog unchanged.", "No root applies."],
    ))

    add(P(
        "longest-word-built-from-others", "Longest Word In Dictionary", "medium", T + ["Strings"], TR,
        "Print the longest word of `wordsList` such that every one of its non-empty prefixes is also in the "
        "list. Break ties by choosing the lexicographically smallest such word. Print an empty line if "
        "none qualifies.",
        [p_words()], OUT_STR, lambda wordsList: _longest_buildable(wordsList),
        [(["a", "ab", "abc", "x"],), (["ab", "cd"],)],
        lambda rng: [(_prefix_closed(rng, count),) for count in (1, 2, 4, 9, 25, 70)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 100"],
        ["Put the words in a set, then test each word's prefixes.",
         "A trie lets you verify all prefixes in one downward walk by checking every marker.",
         "Sort candidates by (-length, word) to apply the tie-break."],
        explanations=["abc has prefixes a and ab present.", "Neither has its single-letter prefix."],
    ))

    add(P(
        "count-trie-nodes", "Count Trie Nodes", "medium", T + ["Strings"], TR,
        "Insert every word of `wordsList` into a trie and print how many nodes it contains, excluding the "
        "root. Shared prefixes share nodes.",
        [p_words()], OUT_INT,
        lambda wordsList: len({w[:i] for w in wordsList for i in range(1, len(w) + 1)}),
        [(["ab", "ac"],), (["a", "a"],)],
        g_words(),
        ["1 <= number of words <= 1000", "1 <= |word| <= 100"],
        ["Each node corresponds to a distinct prefix of some inserted word.",
         "So the count is the number of distinct non-empty prefixes.",
         "Duplicate words add no new nodes."],
        explanations=["Nodes a, ab and ac give 3.", "Only node a exists."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _lcp(wordsList):
    shortest = min(wordsList, key=len)
    for index, ch in enumerate(shortest):
        for other in wordsList:
            if other[index] != ch:
                return shortest[:index]
    return shortest


def _prefix_family(rng, count):
    base = word(rng, rng.randint(1, 3), SMALL)
    result = []
    for _ in range(count):
        if rng.random() < 0.7:
            result.append(base + word(rng, rng.randint(0, 3), SMALL))
        else:
            result.append(word(rng, rng.randint(1, 5), SMALL))
    return result


def _distinct_words(rng, count):
    seen: set[str] = set()
    while len(seen) < count:
        seen.add(word(rng, rng.randint(1, 5), SMALL))
        if len(seen) >= 3 ** 5:
            break
    return sorted(seen)


def _unique_prefix_lengths(wordsList):
    counts: dict[str, int] = {}
    for item in wordsList:
        for length in range(1, len(item) + 1):
            prefix = item[:length]
            counts[prefix] = counts.get(prefix, 0) + 1

    result = []
    for item in wordsList:
        chosen = len(item)
        for length in range(1, len(item) + 1):
            if counts[item[:length]] == 1:
                chosen = length
                break
        result.append(chosen)
    return result


def _unique_prefix_brute(wordsList):
    result = []
    for item in wordsList:
        chosen = len(item)
        for length in range(1, len(item) + 1):
            prefix = item[:length]
            if not any(other != item and other.startswith(prefix) for other in wordsList):
                chosen = length
                break
        result.append(chosen)
    return result


def _matches(candidate, pattern):
    if len(candidate) != len(pattern):
        return False
    return all(p == "." or p == c for c, p in zip(candidate, pattern))


def _max_xor(nums):
    best = 0
    prefixes: set[int] = set()
    for bit in range(20, -1, -1):
        best <<= 1
        prefixes = {value >> bit for value in nums}
        candidate = best | 1
        if any(candidate ^ prefix in prefixes for prefix in prefixes):
            best = candidate
    return best


def _count_prefix_pairs(wordsList):
    from collections import Counter

    counts = Counter(wordsList)
    total = 0
    for item, item_count in counts.items():
        for length in range(1, len(item) + 1):
            prefix = item[:length]
            if prefix == item:
                # Other identical words also prefix this one.
                total += item_count * (item_count - 1)
            elif prefix in counts:
                total += counts[prefix] * item_count
    return total


def _replace_with_roots(roots, wordsList):
    root_set = set(roots)
    result = []
    for item in wordsList:
        replacement = item
        for length in range(1, len(item) + 1):
            if item[:length] in root_set:
                replacement = item[:length]
                break
        result.append(replacement)
    return result


def _longest_buildable(wordsList):
    available = set(wordsList)
    best = ""
    for item in sorted(set(wordsList)):
        if all(item[:length] in available for length in range(1, len(item) + 1)):
            if len(item) > len(best):
                best = item
    return best


def _prefix_closed(rng, count):
    base = word(rng, rng.randint(1, 4), SMALL)
    result = [base[:length] for length in range(1, len(base) + 1)]
    while len(result) < count:
        result.append(word(rng, rng.randint(1, 4), SMALL))
    return result[:count]
