"""String manipulation, parsing and pattern problems."""

from __future__ import annotations

import random
from collections import Counter

from app.content.codequest.framework import (
    INT,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR,
    OUT_STR_LIST,
    P,
    Param,
    STR,
    STR_LIST,
    p_int,
    p_str,
    word,
    words,
)

T = ["Strings"]
SIMS = ["String Simulation"]
HASH = ["Hashing / Frequency"]
TWO = ["Two Pointers"]

LOWER = "abcdefghijklmnopqrstuvwxyz"
SMALL = "abc"
TINY = "ab"
C_S = ["1 <= |s| <= 2000", "s contains lowercase English letters only"]


def g_word(alphabet=LOWER, sizes=(1, 2, 3, 5, 8, 14, 40, 120)):
    def gen(rng: random.Random):
        return [(word(rng, n, alphabet),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "reverse-string", "Reverse String", "easy", T, TWO,
        "Given a string `s`, print its characters in reverse order.",
        [p_str("s")], OUT_STR, lambda s: s[::-1],
        [("hello",), ("a",)], g_word(),
        C_S, ["Swap the outermost characters and work inwards.",
              "Two pointers meeting in the middle need no extra memory.",
              "A single character string is its own reverse."],
        explanations=["hello reversed is olleh.", "One character stays the same."],
    ))

    add(P(
        "is-palindrome-string", "Palindrome String", "easy", T, TWO,
        "Given a string `s`, print `YES` if it reads the same forwards and backwards, else `NO`.",
        [p_str("s")], OUT_BOOL, lambda s: s == s[::-1],
        [("racecar",), ("abca",)],
        lambda rng: [(word(rng, n, SMALL) if rng.random() < 0.5 else _make_palindrome(rng, n),)
                     for n in (1, 2, 3, 4, 7, 12, 30, 80)],
        C_S, ["Compare the character at the front with the one at the back.",
              "Move both pointers inwards until they cross.",
              "Stop early on the first mismatch."],
    ))

    add(P(
        "count-vowels", "Count Vowels", "easy", T, SIMS,
        "Given a string `s`, print how many of its characters are vowels (`a`, `e`, `i`, `o`, `u`).",
        [p_str("s")], OUT_INT, lambda s: sum(1 for ch in s if ch in "aeiou"),
        [("education",), ("xyz",)], g_word(),
        C_S, ["Keep a set of the five vowels for O(1) lookups.",
              "Scan once, incrementing when the character is in that set.",
              "Print 0 when there are no vowels."],
    ))

    add(P(
        "count-consonants", "Count Consonants", "easy", T, SIMS,
        "Given a string `s`, print how many of its characters are consonants (letters that are not vowels).",
        [p_str("s")], OUT_INT, lambda s: sum(1 for ch in s if ch not in "aeiou"),
        [("education",), ("aeiou",)], g_word(),
        C_S, ["A consonant is any letter that is not a vowel.",
              "Count the complement of the vowel set.",
              "Vowels plus consonants must equal the string length."],
    ))

    add(P(
        "character-frequency", "Character Frequency", "easy", T + ["Hashing"], HASH,
        "Given a string `s` and a character `c`, print how many times `c` occurs in `s`.",
        [p_str("s"), Param("c", STR, "a single lowercase letter")], OUT_INT,
        lambda s, c: s.count(c),
        [("banana", "a"), ("abc", "z")],
        lambda rng: [(word(rng, n, SMALL), rng.choice(SMALL)) for n in (1, 3, 6, 12, 30, 90)],
        C_S + ["c is a single lowercase English letter"],
        ["A single counter suffices.", "Compare each character with c.", "Print 0 when c never appears."],
    ))

    add(P(
        "most-frequent-character", "Most Frequent Character", "easy", T + ["Hashing"], HASH,
        "Given a string `s`, print the character that occurs most often. If several tie, print the "
        "alphabetically smallest of them.",
        [p_str("s")], OUT_STR, lambda s: _most_frequent_char(s),
        [("banana",), ("ba",)], g_word(SMALL),
        C_S, ["Count each character with a map or a 26-slot array.",
              "Scan the counts to find the maximum.",
              "Iterate letters in alphabetical order so ties resolve to the smallest automatically."],
        explanations=["a occurs 3 times.", "a and b both occur once, so a wins."],
    ))

    add(P(
        "first-non-repeating-char", "First Unique Character", "easy", T + ["Hashing"], HASH,
        "Given a string `s`, print the first character that occurs exactly once. Print `-1` if every "
        "character repeats.",
        [p_str("s")], OUT_STR, lambda s: _first_unique(s),
        [("leetcode",), ("aabb",)], g_word(SMALL),
        C_S, ["Count frequencies in a first pass.",
              "Scan the string again and return the first character with count 1.",
              "Two passes keep this O(n); one pass cannot know future counts."],
        explanations=["l occurs once and comes first.", "Every character repeats."],
    ))

    add(P(
        "are-anagrams", "Valid Anagram", "easy", T + ["Hashing"], HASH,
        "Given two strings `a` and `b`, print `YES` if one is an anagram of the other (same characters "
        "with the same counts), else `NO`.",
        [Param("a", STR, "first string"), Param("b", STR, "second string")], OUT_BOOL,
        lambda a, b: Counter(a) == Counter(b),
        [("listen", "silent"), ("rat", "car")],
        lambda rng: [(_anagram_pair(rng, n)) for n in (1, 2, 3, 5, 8, 15, 40)],
        ["1 <= |a|, |b| <= 2000", "both strings contain lowercase English letters only"],
        ["Different lengths can never be anagrams — check that first.",
         "Compare character counts rather than sorting, for O(n).",
         "Sorting both strings and comparing also works in O(n log n)."],
    ))

    add(P(
        "sort-string-characters", "Sort String", "easy", T + ["Sorting & Searching"], ["Sorting"],
        "Given a string `s`, print its characters in non-decreasing alphabetical order.",
        [p_str("s")], OUT_STR, lambda s: "".join(sorted(s)),
        [("banana",), ("z",)], g_word(),
        C_S, ["Any comparison sort works.",
              "Counting sort over the 26 letters is O(n) and simple here.",
              "Rebuild the string from the sorted characters."],
    ))

    add(P(
        "remove-duplicate-characters", "Remove Duplicate Characters", "easy", T + ["Hashing"], HASH,
        "Given a string `s`, remove later occurrences of characters already seen, keeping the first "
        "occurrence of each. Print the result.",
        [p_str("s")], OUT_STR, lambda s: _dedupe_keep_first(s),
        [("programming",), ("aaa",)], g_word(SMALL),
        C_S, ["Track which characters you have already emitted in a set.",
              "Append a character only the first time you see it.",
              "The relative order of first occurrences must be preserved."],
        explanations=["programming keeps p,r,o,g,a,m,i,n.", "Only the first a survives."],
    ))

    add(P(
        "longest-common-prefix", "Longest Common Prefix", "easy", T, SIMS,
        "Given a list of strings `strs`, print their longest common prefix. Print an empty line if "
        "there is none.",
        [Param("strs", STR_LIST, "the strings")], OUT_STR,
        lambda strs: _lcp(strs),
        [(["flower", "flow", "flight"],), (["dog", "car"],)],
        lambda rng: [(_prefix_group(rng, count),) for count in (1, 2, 3, 5, 8, 20)],
        ["1 <= number of strings <= 500", "1 <= |strs[i]| <= 200", "lowercase English letters only"],
        ["Compare characters column by column across all strings.",
         "Stop at the first column where any string differs or ends.",
         "The answer can never be longer than the shortest string."],
        explanations=["All three start with fl.", "They share nothing, so print an empty line."],
        brute=lambda strs: _lcp_brute(strs),
    ))

    add(P(
        "string-compression-rle", "Run Length Encoding", "easy", T, SIMS,
        "Compress `s` by replacing each run of a repeated character with the character followed by its "
        "run length. Runs of length 1 keep the count `1`. Print the encoded string.",
        [p_str("s")], OUT_STR, lambda s: _rle(s),
        [("aaabbc",), ("abc",)], g_word(TINY),
        C_S, ["Walk the string tracking the current character and its run length.",
              "Emit the character and the count whenever the run ends.",
              "Do not forget to emit the final run after the loop."],
        explanations=["Three a's, two b's, one c.", "Every run has length 1."],
    ))

    add(P(
        "string-decompression-rle", "Run Length Decoding", "easy", T, SIMS,
        "The string `s` is an encoding where each lowercase letter is followed by a single digit "
        "giving its repeat count. Print the decoded string.",
        [Param("s", STR, "letter/digit pairs, e.g. a3b2")], OUT_STR,
        lambda s: "".join(s[i] * int(s[i + 1]) for i in range(0, len(s), 2)),
        [("a3b2",), ("c1",)],
        lambda rng: [("".join(rng.choice(SMALL) + str(rng.randint(1, 9)) for _ in range(k)),)
                     for k in (1, 2, 3, 5, 9, 20, 60)],
        ["s has even length and 2 <= |s| <= 2000",
         "characters at even positions are lowercase letters, odd positions are digits 1-9"],
        ["Read the string two characters at a time.",
         "Repeat the letter as many times as the digit says.",
         "Digits are always a single character, so no multi-digit parsing is needed."],
    ))

    add(P(
        "to-uppercase", "To Uppercase", "easy", T, SIMS,
        "Given a lowercase string `s`, print it in uppercase.",
        [p_str("s")], OUT_STR, lambda s: s.upper(),
        [("hello",), ("z",)], g_word(),
        C_S, ["Uppercase letters sit 32 code points below lowercase in ASCII.",
              "Subtract 32 from each character code, or use the language's built-in.",
              "Only letters change."],
    ))

    add(P(
        "toggle-case-alternating", "Alternating Case", "easy", T, SIMS,
        "Given a lowercase string `s`, print it with characters at even positions uppercased and "
        "characters at odd positions left lowercase (positions are 0-based).",
        [p_str("s")], OUT_STR,
        lambda s: "".join(ch.upper() if i % 2 == 0 else ch for i, ch in enumerate(s)),
        [("hello",), ("ab",)], g_word(),
        C_S, ["Use the index parity to decide the case.",
              "Index 0 is even, so the first character is uppercased.",
              "Build the result as you scan."],
    ))

    add(P(
        "count-words", "Count Words", "easy", T, SIMS,
        "Given a list of `n` words, print how many of them have length strictly greater than `k`.",
        [Param("wordsList", STR_LIST, "the words"), p_int("k", "length threshold")], OUT_INT,
        lambda wordsList, k: sum(1 for w in wordsList if len(w) > k),
        [(["apple", "at", "banana"], 3), (["hi"], 5)],
        lambda rng: [(words(rng, count, 1, 8), rng.randint(0, 6)) for count in (1, 2, 4, 9, 25, 80)],
        ["1 <= n <= 1000", "1 <= |word| <= 200", "0 <= k <= 200"],
        ["Compare each word's length against k.", "The comparison is strict (> k, not >= k).",
         "Print 0 when no word qualifies."],
    ))

    add(P(
        "longest-word", "Longest Word", "easy", T, SIMS,
        "Given a list of words, print the longest one. If several share the maximum length, print the "
        "one that appears first.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR,
        lambda wordsList: max(wordsList, key=len),
        [(["cat", "banana", "kiwi"],), (["ab", "cd"],)],
        lambda rng: [(words(rng, count, 1, 9),) for count in (1, 2, 4, 8, 20, 60)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Track the best word and its length.",
         "Only replace the best when you find a strictly longer word, so ties keep the earlier one.",
         "One pass is enough."],
        explanations=["banana has 6 characters.", "Both have 2, so the first one wins."],
    ))

    add(P(
        "reverse-words-order", "Reverse Word Order", "easy", T, SIMS,
        "Given a list of `n` words, print them in reverse order, one per line.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR_LIST,
        lambda wordsList: list(reversed(wordsList)),
        [(["the", "sky", "is", "blue"],), (["one"],)],
        lambda rng: [(words(rng, count, 1, 6),) for count in (1, 2, 3, 6, 15, 50)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Reverse the list, not the characters inside each word.",
         "Print one word per line.",
         "A single word is unchanged."],
    ))

    add(P(
        "reverse-each-word", "Reverse Each Word", "easy", T, SIMS,
        "Given a list of `n` words, print each word with its characters reversed, keeping the words "
        "in their original order, one per line.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR_LIST,
        lambda wordsList: [w[::-1] for w in wordsList],
        [(["abc", "de"],), (["x"],)],
        lambda rng: [(words(rng, count, 1, 7),) for count in (1, 2, 4, 9, 25, 70)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Reverse the characters of each word independently.",
         "Word order stays the same.",
         "Handle single-character words naturally."],
    ))

    add(P(
        "is-rotation-of-string", "String Rotation", "easy", T, SIMS,
        "Given two strings `a` and `b`, print `YES` if `b` is a rotation of `a` (obtained by moving "
        "some prefix of `a` to its end), else `NO`.",
        [Param("a", STR, "first string"), Param("b", STR, "second string")], OUT_BOOL,
        lambda a, b: len(a) == len(b) and b in (a + a),
        [("abcde", "cdeab"), ("abc", "acb")],
        lambda rng: [(_rotation_pair(rng, n)) for n in (1, 2, 3, 5, 8, 16, 40)],
        ["1 <= |a|, |b| <= 2000", "lowercase English letters only"],
        ["Rotations of a all appear as substrings of a + a.",
         "Check the lengths match before searching.",
         "So the whole test is: same length and b is a substring of a+a."],
        explanations=["Moving ab to the end of abcde gives cdeab.",
                      "acb is a permutation but not a rotation."],
        brute=lambda a, b: len(a) == len(b) and any(a[i:] + a[:i] == b for i in range(len(a))),
    ))

    add(P(
        "substring-search-index", "Find Substring", "easy", T, SIMS,
        "Given strings `s` and `pattern`, print the index of the first occurrence of `pattern` in `s`, "
        "or `-1` if it does not occur.",
        [Param("s", STR, "the text"), Param("pattern", STR, "the pattern to find")], OUT_INT,
        lambda s, pattern: s.find(pattern),
        [("hayneedlestack", "needle"), ("abc", "xyz")],
        lambda rng: [(_pattern_pair(rng, n)) for n in (1, 2, 4, 8, 16, 40, 100)],
        ["1 <= |s| <= 2000", "1 <= |pattern| <= 2000", "lowercase English letters only"],
        ["The straightforward approach tries every starting index — O(n*m).",
         "KMP builds a prefix-function to skip re-comparisons and runs in O(n+m).",
         "Return the first match, and -1 when there is none."],
        brute=lambda s, pattern: next((i for i in range(len(s) - len(pattern) + 1)
                                       if s[i:i + len(pattern)] == pattern), -1),
    ))

    add(P(
        "count-substring-occurrences", "Count Substring Occurrences", "easy", T, SIMS,
        "Given strings `s` and `pattern`, count how many times `pattern` appears in `s`. Overlapping "
        "occurrences are counted separately.",
        [Param("s", STR, "the text"), Param("pattern", STR, "the pattern")], OUT_INT,
        lambda s, pattern: sum(1 for i in range(len(s) - len(pattern) + 1)
                               if s[i:i + len(pattern)] == pattern),
        [("aaaa", "aa"), ("abc", "d")],
        lambda rng: [(word(rng, n, TINY), word(rng, rng.randint(1, 3), TINY)) for n in (1, 3, 6, 12, 30, 80)],
        ["1 <= |s| <= 2000", "1 <= |pattern| <= 2000", "lowercase English letters only"],
        ["Slide a window of the pattern's length across s.",
         "Overlaps count, so advance by one position, not by the pattern length.",
         "KMP gives all occurrences in linear time."],
        explanations=["aa occurs at indices 0, 1 and 2.", "d never appears."],
    ))

    add(P(
        "longest-palindromic-substring-len", "Longest Palindromic Substring", "medium", T, TWO,
        "Given a string `s`, print the length of its longest palindromic substring.",
        [p_str("s")], OUT_INT, lambda s: _longest_palindrome_len(s),
        [("babad",), ("abcd",)], g_word(SMALL, (1, 2, 3, 5, 9, 16, 40, 90)),
        C_S, ["Expand around every centre — there are 2n-1 centres counting the gaps between characters.",
              "Handle odd-length and even-length palindromes separately.",
              "This is O(n^2) time and O(1) space; Manacher's algorithm achieves O(n).",
              "A single character is already a palindrome of length 1."],
        explanations=["bab and aba both have length 3.", "No palindrome longer than one character."],
        brute=lambda s: max(len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                            if s[i:j] == s[i:j][::-1]),
    ))

    add(P(
        "count-palindromic-substrings", "Count Palindromic Substrings", "medium", T, TWO,
        "Given a string `s`, count its palindromic substrings. Substrings at different positions count "
        "separately even if they look the same.",
        [p_str("s")], OUT_INT, lambda s: _count_palindromes(s),
        [("aaa",), ("abc",)], g_word(TINY, (1, 2, 3, 5, 8, 14, 35, 80)),
        C_S, ["Expand around each of the 2n-1 centres, counting every successful expansion.",
              "Each single character contributes one palindrome.",
              "Total is O(n^2) which is fine for these limits."],
        explanations=["a, a, a, aa, aa, aaa gives 6.", "Only the three single characters qualify."],
        brute=lambda s: sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                            if s[i:j] == s[i:j][::-1]),
    ))

    add(P(
        "longest-substring-without-repeat", "Longest Substring Without Repeating Characters", "medium",
        T + ["Sliding Window", "Hashing"], ["Sliding Window"],
        "Given a string `s`, print the length of the longest substring that contains no repeated "
        "character.",
        [p_str("s")], OUT_INT, lambda s: _longest_unique_window(s),
        [("abcabcbb",), ("bbbb",)], g_word(SMALL, (1, 2, 4, 8, 16, 40, 100, 250)),
        C_S, ["Slide a window and keep the characters inside it in a set.",
              "When the incoming character is already inside, shrink from the left until it is not.",
              "Storing each character's last index lets the left edge jump directly.",
              "Track the best window length as you go."],
        explanations=["abc has length 3.", "Only a single b can be taken."],
        brute=lambda s: max((j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                             if len(set(s[i:j])) == j - i), default=0),
        pattern_note="The sliding-window template: grow the right edge, and while the window is invalid, "
                     "shrink the left edge. Every index enters and leaves at most once, so it is O(n).",
    ))

    add(P(
        "check-permutation-substring", "Permutation In String", "medium",
        T + ["Sliding Window", "Hashing"], ["Sliding Window"],
        "Given strings `s` and `pattern`, print `YES` if some substring of `s` is a permutation of "
        "`pattern`, else `NO`.",
        [Param("s", STR, "the text"), Param("pattern", STR, "the pattern")], OUT_BOOL,
        lambda s, pattern: _has_permutation(s, pattern),
        [("eidbaooo", "ab"), ("abc", "xyz")],
        lambda rng: [(word(rng, n, SMALL), word(rng, rng.randint(1, 4), SMALL)) for n in (1, 3, 6, 12, 30, 80)],
        ["1 <= |s| <= 2000", "1 <= |pattern| <= 2000", "lowercase English letters only"],
        ["Any permutation has the same character counts, so compare frequency windows.",
         "Slide a window of length |pattern| and maintain its counts incrementally.",
         "Comparing 26-slot count arrays is O(1) per step.",
         "Answer NO immediately when |pattern| > |s|."],
        explanations=["ba at index 3 is a permutation of ab.", "No window matches."],
        brute=lambda s, pattern: any(Counter(s[i:i + len(pattern)]) == Counter(pattern)
                                     for i in range(len(s) - len(pattern) + 1)),
    ))

    add(P(
        "group-anagrams-count", "Count Anagram Groups", "medium", T + ["Hashing"], HASH,
        "Given a list of words, group the anagrams together and print how many distinct groups there are.",
        [Param("wordsList", STR_LIST, "the words")], OUT_INT,
        lambda wordsList: len({"".join(sorted(w)) for w in wordsList}),
        [(["eat", "tea", "tan", "ate", "nat", "bat"],), (["abc"],)],
        lambda rng: [(words(rng, count, 1, 4, SMALL),) for count in (1, 2, 4, 9, 25, 70)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Words are anagrams exactly when their sorted characters match.",
         "Use the sorted string as a hash key.",
         "The answer is the number of distinct keys."],
        explanations=["Groups are {eat,tea,ate}, {tan,nat} and {bat}.", "One word means one group."],
    ))

    add(P(
        "largest-anagram-group-size", "Largest Anagram Group", "medium", T + ["Hashing"], HASH,
        "Given a list of words, print the size of the largest group of words that are anagrams of "
        "one another.",
        [Param("wordsList", STR_LIST, "the words")], OUT_INT,
        lambda wordsList: max(Counter("".join(sorted(w)) for w in wordsList).values()),
        [(["eat", "tea", "tan", "ate"],), (["ab", "cd"],)],
        lambda rng: [(words(rng, count, 1, 3, SMALL),) for count in (1, 2, 5, 10, 30, 80)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Bucket words by their sorted form.", "The answer is the largest bucket size.",
         "Every word forms at least a group of one."],
    ))

    add(P(
        "isomorphic-strings", "Isomorphic Strings", "easy", T + ["Hashing"], HASH,
        "Two strings are isomorphic when characters of the first can be replaced consistently to get "
        "the second, with no two characters mapping to the same character. Print `YES` or `NO`.",
        [Param("a", STR, "first string"), Param("b", STR, "second string")], OUT_BOOL,
        lambda a, b: _isomorphic(a, b),
        [("egg", "add"), ("foo", "bar")],
        lambda rng: [(word(rng, n, SMALL), word(rng, n, SMALL)) for n in (1, 2, 3, 5, 9, 20, 60)],
        ["1 <= |a| = |b| <= 2000", "lowercase English letters only"],
        ["Maintain two maps: one from a to b and one from b to a.",
         "A conflict in either direction means the answer is NO.",
         "The bijection requirement is why one map is not enough — foo/bar fails only in one direction.",
         "Different lengths are never isomorphic."],
        explanations=["e->a and g->d works.", "f->b but both o's would need to map to a and r."],
    ))

    add(P(
        "valid-parentheses-string", "Valid Parentheses", "easy", T + ["Stack & Queue"], ["Stack / Queue"],
        "Given a string `s` containing only the characters `(`, `)`, `[`, `]`, `{` and `}`, print "
        "`YES` if the brackets are correctly matched and nested, else `NO`.",
        [Param("s", STR, "bracket characters only")], OUT_BOOL,
        lambda s: _valid_brackets(s),
        [("()[]{}",), ("([)]",)],
        lambda rng: [(_bracket_string(rng, n),) for n in (1, 2, 4, 6, 10, 20, 50, 120)],
        ["1 <= |s| <= 2000", "s contains only the characters ()[]{}"],
        ["Push every opening bracket onto a stack.",
         "On a closing bracket, the stack top must be the matching opener — otherwise fail.",
         "The string is valid only if the stack is empty at the end.",
         "An odd-length string can never be valid."],
        explanations=["Each pair closes immediately.", "The brackets cross instead of nesting."],
    ))

    add(P(
        "longest-valid-parentheses", "Longest Valid Parentheses", "hard",
        T + ["Stack & Queue", "Dynamic Programming"], ["Stack / Queue"],
        "Given a string `s` of only `(` and `)`, print the length of the longest substring that is a "
        "valid parentheses sequence.",
        [Param("s", STR, "only ( and ) characters")], OUT_INT,
        lambda s: _longest_valid_parens(s),
        [("(()",), (")()())",)],
        lambda rng: [("".join(rng.choice("()") for _ in range(n)),) for n in (1, 2, 4, 8, 15, 35, 90, 200)],
        ["1 <= |s| <= 2000", "s contains only ( and )"],
        ["Keep a stack of indices, seeded with -1 as a base.",
         "On '(' push the index; on ')' pop, and if the stack empties push the current index as the new base.",
         "After a successful pop, the current length is index - stackTop.",
         "A two-pass counting scan (left-to-right then right-to-left) also works in O(1) space."],
        explanations=["() at indices 1-2 has length 2.", "()() at indices 1-4 has length 4."],
        brute=lambda s: max((j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                             if _valid_brackets(s[i:j])), default=0),
    ))

    add(P(
        "remove-vowels", "Remove Vowels", "easy", T, SIMS,
        "Given a string `s`, print it with every vowel removed. Print an empty line if nothing remains.",
        [p_str("s")], OUT_STR, lambda s: "".join(ch for ch in s if ch not in "aeiou"),
        [("education",), ("aei",)], g_word(),
        C_S, ["Filter out characters that belong to the vowel set.",
              "Preserve the order of the remaining characters.",
              "The result may be empty."],
    ))

    add(P(
        "capitalize-first-letters", "Capitalize Words", "easy", T, SIMS,
        "Given a list of lowercase words, print each with its first letter uppercased, one per line.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR_LIST,
        lambda wordsList: [w[0].upper() + w[1:] for w in wordsList],
        [(["hello", "world"],), (["a"],)],
        lambda rng: [(words(rng, count, 1, 8),) for count in (1, 2, 5, 12, 30, 80)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Uppercase index 0 and append the rest unchanged.",
         "Single-character words become a single uppercase letter.",
         "Print one word per line."],
    ))

    add(P(
        "string-to-integer", "String To Integer", "easy", T + ["Math"], SIMS,
        "The string `s` holds an optional leading `-` followed by digits. Print the integer it "
        "represents, without using your language's built-in string-to-integer conversion.",
        [Param("s", STR, "optional '-' then digits")], OUT_INT,
        lambda s: _atoi(s),
        [("-1234",), ("70",)],
        lambda rng: [(("-" if rng.random() < 0.4 else "") + str(rng.randint(0, 10 ** rng.randint(1, 6))),)
                     for _ in range(8)],
        ["1 <= |s| <= 12", "s matches -?[0-9]+", "the value fits in a 64-bit signed integer"],
        ["Process digits left to right: value = value * 10 + digit.",
         "Convert a digit character with (ch - '0').",
         "Apply the sign at the end if the first character was '-'."],
    ))

    add(P(
        "integer-to-string", "Integer To String", "easy", T + ["Math"], SIMS,
        "Given an integer `n`, print its decimal representation without using your language's built-in "
        "number-to-string conversion.",
        [p_int("n")], OUT_STR, lambda n: str(n),
        [(-405,), (0,)],
        lambda rng: [(rng.choice([1, -1]) * rng.randint(0, 10 ** rng.randint(1, 7)),) for _ in range(8)],
        ["-10^9 <= n <= 10^9"],
        ["Repeatedly take n % 10 to peel off the last digit, then divide by 10.",
         "Digits come out reversed, so reverse them at the end.",
         "Handle n = 0 explicitly, and emit '-' for negatives."],
    ))

    add(P(
        "count-distinct-characters", "Count Distinct Characters", "easy", T + ["Hashing"], HASH,
        "Given a string `s`, print how many distinct characters it contains.",
        [p_str("s")], OUT_INT, lambda s: len(set(s)),
        [("banana",), ("abcd",)], g_word(),
        C_S, ["Insert every character into a set.", "The answer is the set's size.",
              "A 26-slot boolean array works too and is faster."],
    ))

    add(P(
        "has-all-unique-characters", "All Characters Unique", "easy", T + ["Hashing"], HASH,
        "Given a string `s`, print `YES` if every character is distinct, else `NO`.",
        [p_str("s")], OUT_BOOL, lambda s: len(set(s)) == len(s),
        [("abcd",), ("aab",)], g_word(SMALL),
        C_S, ["Compare the number of distinct characters against the length.",
              "Or stop early the first time a character repeats.",
              "Strings longer than 26 characters must repeat."],
    ))

    add(P(
        "is-pangram", "Pangram Check", "easy", T + ["Hashing"], HASH,
        "Given a lowercase string `s`, print `YES` if it contains every letter of the English alphabet "
        "at least once, else `NO`.",
        [p_str("s")], OUT_BOOL, lambda s: len(set(s)) == 26,
        [("thequickbrownfoxjumpsoverthelazydog",), ("abc",)],
        lambda rng: [((LOWER + word(rng, rng.randint(0, 10))) if rng.random() < 0.4 else word(rng, n),)
                     for n in (1, 5, 20, 26, 60, 150)],
        ["1 <= |s| <= 2000", "s contains lowercase English letters only"],
        ["Collect the distinct characters.", "The string is a pangram when 26 distinct letters appear.",
         "A string shorter than 26 characters can never qualify."],
    ))

    add(P(
        "caesar-cipher-shift", "Caesar Cipher", "easy", T + ["Math"], SIMS,
        "Shift every character of the lowercase string `s` forward by `k` positions in the alphabet, "
        "wrapping from `z` back to `a`. Print the result.",
        [p_str("s"), p_int("k", "shift amount")], OUT_STR,
        lambda s, k: "".join(chr((ord(ch) - 97 + k) % 26 + 97) for ch in s),
        [("abc", 2), ("xyz", 3)],
        lambda rng: [(word(rng, n), rng.randint(0, 100)) for n in (1, 2, 5, 10, 30, 90)],
        ["1 <= |s| <= 2000", "0 <= k <= 1000", "s contains lowercase English letters only"],
        ["Map each character to 0..25, add k, then take the remainder modulo 26.",
         "Convert back by adding the code of 'a'.",
         "Reducing k modulo 26 first avoids large arithmetic."],
        explanations=["abc shifted by 2 gives cde.", "xyz wraps around to abc."],
    ))

    add(P(
        "count-character-pairs-equal", "Count Equal Adjacent Pairs", "easy", T, SIMS,
        "Given a string `s`, count the positions `i` where `s[i] == s[i+1]`.",
        [p_str("s")], OUT_INT,
        lambda s: sum(1 for i in range(len(s) - 1) if s[i] == s[i + 1]),
        [("aabbb",), ("abc",)], g_word(TINY),
        C_S, ["Compare each character with the next one.",
              "Stop the loop at index n-2 to stay in bounds.",
              "A run of length L contributes L-1 pairs."],
        explanations=["Pairs at indices 0, 2 and 3.", "No two neighbours match."],
    ))

    add(P(
        "lexicographically-smallest-word", "Lexicographically Smallest Word", "easy",
        T + ["Sorting & Searching"], ["Sorting"],
        "Given a list of words, print the lexicographically smallest one.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR,
        lambda wordsList: min(wordsList),
        [(["banana", "apple", "cherry"],), (["b", "a"],)],
        lambda rng: [(words(rng, count, 1, 6),) for count in (1, 2, 5, 12, 30, 90)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["String comparison is character by character.",
         "A prefix is smaller than any string that extends it.",
         "A single pass tracking the current smallest is enough."],
    ))

    add(P(
        "sort-words-by-length", "Sort Words By Length", "easy", T + ["Sorting & Searching"], ["Sorting"],
        "Sort the given words by increasing length, breaking ties alphabetically, and print them one "
        "per line.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR_LIST,
        lambda wordsList: sorted(wordsList, key=lambda w: (len(w), w)),
        [(["pear", "fig", "apple", "kiwi"],), (["bb", "aa"],)],
        lambda rng: [(words(rng, count, 1, 6),) for count in (1, 2, 5, 12, 35, 90)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Sort with a composite key: length first, then the word itself.",
         "The tie-break makes the output unique.",
         "Most languages support tuple keys directly."],
        explanations=["fig (3), kiwi and pear (4), apple (5).", "Same length, so alphabetical."],
    ))

    add(P(
        "string-rotation-lexicographically-smallest", "Smallest Rotation", "medium", T, SIMS,
        "Print the lexicographically smallest rotation of the string `s`.",
        [p_str("s")], OUT_STR,
        lambda s: min(s[i:] + s[:i] for i in range(len(s))),
        [("bcda",), ("aaa",)], g_word(SMALL, (1, 2, 3, 5, 9, 18, 45, 100)),
        C_S, ["There are exactly |s| rotations.",
              "Generating them all and taking the minimum is O(n^2) and passes these limits.",
              "Booth's algorithm finds the answer in O(n).",
              "Concatenating s with itself makes each rotation a window of length |s|."],
        explanations=["Rotations include abcd, which is smallest.", "All rotations are identical."],
    ))

    add(P(
        "minimum-deletions-to-palindrome", "Deletions To Make Palindrome", "medium",
        T + ["Dynamic Programming"], ["Dynamic Programming"],
        "Print the minimum number of characters to delete from `s` so the remaining string is a "
        "palindrome.",
        [p_str("s")], OUT_INT, lambda s: len(s) - _lps_length(s),
        [("aebcbda",), ("abc",)], g_word(SMALL, (1, 2, 3, 5, 8, 14, 30, 60)),
        C_S, ["The characters you keep form the longest palindromic subsequence.",
              "So the answer is |s| minus the length of that subsequence.",
              "The longest palindromic subsequence equals the longest common subsequence of s and its reverse.",
              "Use an O(n^2) DP over substring ranges."],
        explanations=["Deleting e and d leaves abcba.", "Keep one character; delete the other two."],
    ))

    add(P(
        "check-subsequence", "Is Subsequence", "easy", T, TWO,
        "Print `YES` if `a` is a subsequence of `b` (obtainable by deleting some characters of `b` "
        "without reordering), else `NO`.",
        [Param("a", STR, "candidate subsequence"), Param("b", STR, "the source string")], OUT_BOOL,
        lambda a, b: _is_subsequence(a, b),
        [("abc", "ahbgdc"), ("axc", "ahbgdc")],
        lambda rng: [(word(rng, rng.randint(1, 4), SMALL), word(rng, n, SMALL)) for n in (1, 3, 6, 12, 30, 80)],
        ["1 <= |a|, |b| <= 2000", "lowercase English letters only"],
        ["Walk both strings with two pointers.",
         "Advance the pointer into a only when the characters match; always advance the pointer into b.",
         "a is a subsequence exactly when its pointer reaches the end."],
    ))

    add(P(
        "longest-common-subsequence-len", "Longest Common Subsequence", "medium",
        T + ["Dynamic Programming"], ["Dynamic Programming"],
        "Print the length of the longest common subsequence of strings `a` and `b`.",
        [Param("a", STR, "first string"), Param("b", STR, "second string")], OUT_INT,
        lambda a, b: _lcs_length(a, b),
        [("abcde", "ace"), ("abc", "def")],
        lambda rng: [(word(rng, n, SMALL), word(rng, m, SMALL))
                     for n, m in ((1, 1), (2, 3), (5, 4), (8, 9), (15, 12), (30, 28), (60, 55))],
        ["1 <= |a|, |b| <= 500", "lowercase English letters only"],
        ["Let dp[i][j] be the answer for the first i characters of a and the first j of b.",
         "When the current characters match, dp[i][j] = dp[i-1][j-1] + 1.",
         "Otherwise take the better of dropping one character from either string.",
         "Only the previous row is needed, so O(min(n,m)) space suffices."],
        explanations=["ace is common and has length 3.", "Nothing is shared."],
    ))

    add(P(
        "edit-distance", "Edit Distance", "hard", T + ["Dynamic Programming"], ["Dynamic Programming"],
        "Print the minimum number of single-character insertions, deletions or replacements needed to "
        "turn `a` into `b`.",
        [Param("a", STR, "source string"), Param("b", STR, "target string")], OUT_INT,
        lambda a, b: _edit_distance(a, b),
        [("horse", "ros"), ("abc", "abc")],
        lambda rng: [(word(rng, n, SMALL), word(rng, m, SMALL))
                     for n, m in ((1, 1), (2, 3), (4, 6), (8, 7), (14, 15), (30, 25), (55, 60))],
        ["1 <= |a|, |b| <= 500", "lowercase English letters only"],
        ["dp[i][j] is the distance between the first i characters of a and the first j of b.",
         "Matching characters cost nothing: dp[i][j] = dp[i-1][j-1].",
         "Otherwise it is 1 + min(insert, delete, replace) = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1]).",
         "Initialise the first row and column to 0..n, the cost of building from an empty string."],
        explanations=["horse -> rorse -> rose -> ros costs 3.", "The strings already match."],
    ))

    add(P(
        "word-frequency-top", "Most Frequent Word", "easy", T + ["Hashing"], HASH,
        "Given a list of words, print the word that appears most often. Break ties by choosing the "
        "lexicographically smallest word.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR,
        lambda wordsList: min(Counter(wordsList).items(), key=lambda kv: (-kv[1], kv[0]))[0],
        [(["a", "b", "a"],), (["y", "x"],)],
        lambda rng: [(words(rng, count, 1, 3, SMALL),) for count in (1, 3, 6, 15, 40, 100)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Count occurrences with a hash map.",
         "Sort or scan by (-count, word) so ties resolve alphabetically.",
         "Every word appears at least once."],
        explanations=["a appears twice.", "Both appear once, so x wins."],
    ))

    add(P(
        "reverse-vowels-only", "Reverse Vowels", "easy", T, TWO,
        "Reverse only the vowels of the string `s`, leaving every other character in place. Print the "
        "result.",
        [p_str("s")], OUT_STR, lambda s: _reverse_vowels(s),
        [("leetcode",), ("bcd",)], g_word(),
        C_S, ["Collect the vowel positions, or use two pointers that skip consonants.",
              "Swap the outermost vowels, then move inwards.",
              "Consonants never move."],
        explanations=["Vowels e,e,o,e reverse to e,o,e,e giving leotcede.", "There are no vowels to swap."],
    ))

    add(P(
        "shortest-word-length", "Shortest Word Length", "easy", T, SIMS,
        "Given a list of words, print the length of the shortest one.",
        [Param("wordsList", STR_LIST, "the words")], OUT_INT,
        lambda wordsList: min(len(w) for w in wordsList),
        [(["apple", "fig", "kiwi"],), (["abc"],)],
        lambda rng: [(words(rng, count, 1, 9),) for count in (1, 2, 5, 12, 30, 90)],
        ["1 <= n <= 1000", "1 <= |word| <= 200"],
        ["Track the minimum length while scanning.", "Initialise from the first word's length.",
         "Every word has at least one character."],
    ))

    add(P(
        "digits-in-string-sum", "Sum Of Digits In String", "easy", T + ["Math"], SIMS,
        "The string `s` mixes lowercase letters and digits. Print the sum of all digit characters.",
        [Param("s", STR, "letters and digits")], OUT_INT,
        lambda s: sum(int(ch) for ch in s if ch.isdigit()),
        [("a1b2c3",), ("abc",)],
        lambda rng: [("".join(rng.choice(SMALL + "0123456789") for _ in range(n)),)
                     for n in (1, 3, 6, 12, 30, 90)],
        ["1 <= |s| <= 2000", "s contains lowercase letters and digits only"],
        ["Test each character for being a digit.",
         "Convert with (ch - '0') and accumulate.",
         "Print 0 when no digits appear."],
    ))

    add(P(
        "excel-column-title-number", "Excel Column Number", "easy", T + ["Math"], ["Math & Number Theory"],
        "Spreadsheet columns are labelled `a`, `b`, ..., `z`, `aa`, `ab`, ... Given a lowercase label "
        "`s`, print its 1-based column number.",
        [Param("s", STR, "the column label")], OUT_INT,
        lambda s: _column_number(s),
        [("aa",), ("z",)],
        lambda rng: [(word(rng, rng.randint(1, 5)),) for _ in range(8)],
        ["1 <= |s| <= 6", "s contains lowercase English letters only"],
        ["This is base-26 with digits 1..26 rather than 0..25.",
         "value = value * 26 + (ch - 'a' + 1) for each character.",
         "So 'z' is 26 and 'aa' is 27."],
        explanations=["1*26 + 1 = 27.", "z is the 26th column."],
    ))

    add(P(
        "min-window-substring-len", "Minimum Window Substring", "hard",
        T + ["Sliding Window", "Hashing"], ["Sliding Window"],
        "Print the length of the shortest substring of `s` that contains every character of `pattern`, "
        "counting multiplicities. Print `0` if no such substring exists.",
        [Param("s", STR, "the text"), Param("pattern", STR, "required characters")], OUT_INT,
        lambda s, pattern: _min_window(s, pattern),
        [("adobecodebanc", "abc"), ("a", "aa")],
        lambda rng: [(word(rng, n, SMALL), word(rng, rng.randint(1, 4), SMALL)) for n in (1, 3, 6, 14, 35, 90, 200)],
        ["1 <= |s| <= 2000", "1 <= |pattern| <= 2000", "lowercase English letters only"],
        ["Count the characters pattern needs, then slide a window over s.",
         "Track how many required characters are still missing; the window is valid when nothing is missing.",
         "Once valid, shrink from the left while it stays valid, recording the best length.",
         "Each index enters and leaves the window once, giving O(n)."],
        explanations=["banc has length 4 and contains a, b and c.", "s cannot supply two a's."],
        brute=lambda s, pattern: _min_window_brute(s, pattern),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _make_palindrome(rng, n):
    half = word(rng, (n + 1) // 2, SMALL)
    return half + half[::-1][n % 2:]


def _most_frequent_char(s):
    counts = Counter(s)
    best = max(counts.values())
    return min(ch for ch, count in counts.items() if count == best)


def _first_unique(s):
    counts = Counter(s)
    for ch in s:
        if counts[ch] == 1:
            return ch
    return "-1"


def _anagram_pair(rng, n):
    a = word(rng, n, SMALL)
    if rng.random() < 0.5:
        chars = list(a)
        rng.shuffle(chars)
        return (a, "".join(chars))
    return (a, word(rng, n, SMALL))


def _dedupe_keep_first(s):
    seen = set()
    out = []
    for ch in s:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return "".join(out)


def _lcp(strs):
    if not strs:
        return ""
    shortest = min(strs, key=len)
    for index, ch in enumerate(shortest):
        for other in strs:
            if other[index] != ch:
                return shortest[:index]
    return shortest


def _lcp_brute(strs):
    prefix = strs[0]
    for other in strs[1:]:
        while not other.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def _prefix_group(rng, count):
    base = word(rng, rng.randint(1, 4), SMALL)
    result = []
    for _ in range(count):
        if rng.random() < 0.7:
            result.append(base + word(rng, rng.randint(0, 4), SMALL))
        else:
            result.append(word(rng, rng.randint(1, 6), SMALL))
    return result


def _rle(s):
    out = []
    index = 0
    while index < len(s):
        run = index
        while run < len(s) and s[run] == s[index]:
            run += 1
        out.append(f"{s[index]}{run - index}")
        index = run
    return "".join(out)


def _rotation_pair(rng, n):
    a = word(rng, n, SMALL)
    if rng.random() < 0.6:
        shift = rng.randint(0, n - 1)
        return (a, a[shift:] + a[:shift])
    return (a, word(rng, n, SMALL))


def _pattern_pair(rng, n):
    s = word(rng, n, SMALL)
    if rng.random() < 0.6 and n >= 2:
        start = rng.randint(0, n - 2)
        end = rng.randint(start + 1, n)
        return (s, s[start:end])
    return (s, word(rng, rng.randint(1, 3), SMALL))


def _longest_palindrome_len(s):
    best = 0
    for centre in range(len(s)):
        for offset in (0, 1):
            left, right = centre, centre + offset
            while left >= 0 and right < len(s) and s[left] == s[right]:
                best = max(best, right - left + 1)
                left -= 1
                right += 1
    return best


def _count_palindromes(s):
    total = 0
    for centre in range(len(s)):
        for offset in (0, 1):
            left, right = centre, centre + offset
            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1
                left -= 1
                right += 1
    return total


def _longest_unique_window(s):
    last: dict[str, int] = {}
    best = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


def _has_permutation(s, pattern):
    need = Counter(pattern)
    size = len(pattern)
    if size > len(s):
        return False
    window = Counter(s[:size])
    if window == need:
        return True
    for index in range(size, len(s)):
        window[s[index]] += 1
        outgoing = s[index - size]
        window[outgoing] -= 1
        if window[outgoing] == 0:
            del window[outgoing]
        if window == need:
            return True
    return False


def _isomorphic(a, b):
    if len(a) != len(b):
        return False
    forward: dict[str, str] = {}
    backward: dict[str, str] = {}
    for x, y in zip(a, b):
        if forward.setdefault(x, y) != y:
            return False
        if backward.setdefault(y, x) != x:
            return False
    return True


PAIRS = {")": "(", "]": "[", "}": "{"}


def _valid_brackets(s):
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
        else:
            return False
    return not stack


def _bracket_string(rng, n):
    if rng.random() < 0.45:
        # Build a balanced string, then optionally leave it intact.
        out: list[str] = []
        stack: list[str] = []
        for _ in range(n):
            if stack and (len(out) + len(stack) >= n or rng.random() < 0.5):
                out.append({"(": ")", "[": "]", "{": "}"}[stack.pop()])
            else:
                opener = rng.choice("([{")
                stack.append(opener)
                out.append(opener)
        while stack:
            out.append({"(": ")", "[": "]", "{": "}"}[stack.pop()])
        return "".join(out)[:n] or "("
    return "".join(rng.choice("()[]{}") for _ in range(n))


def _longest_valid_parens(s):
    stack = [-1]
    best = 0
    for index, ch in enumerate(s):
        if ch == "(":
            stack.append(index)
        else:
            stack.pop()
            if not stack:
                stack.append(index)
            else:
                best = max(best, index - stack[-1])
    return best


def _atoi(s):
    negative = s[0] == "-"
    value = 0
    for ch in s[1:] if negative else s:
        value = value * 10 + (ord(ch) - 48)
    return -value if negative else value


def _lps_length(s):
    return _lcs_length(s, s[::-1])


def _is_subsequence(a, b):
    index = 0
    for ch in b:
        if index < len(a) and a[index] == ch:
            index += 1
    return index == len(a)


def _lcs_length(a, b):
    previous = [0] * (len(b) + 1)
    for x in a:
        current = [0] * (len(b) + 1)
        for j, y in enumerate(b, start=1):
            current[j] = previous[j - 1] + 1 if x == y else max(previous[j], current[j - 1])
        previous = current
    return previous[len(b)]


def _edit_distance(a, b):
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, start=1):
        current = [i] + [0] * len(b)
        for j, y in enumerate(b, start=1):
            current[j] = previous[j - 1] if x == y else 1 + min(previous[j - 1], previous[j], current[j - 1])
        previous = current
    return previous[len(b)]


def _reverse_vowels(s):
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        if chars[left] not in "aeiou":
            left += 1
        elif chars[right] not in "aeiou":
            right -= 1
        else:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1
    return "".join(chars)


def _column_number(s):
    value = 0
    for ch in s:
        value = value * 26 + (ord(ch) - 96)
    return value


def _min_window(s, pattern):
    need = Counter(pattern)
    missing = len(pattern)
    best = 0
    left = 0
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if best == 0 or right - left + 1 < best:
                best = right - left + 1
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return best


def _min_window_brute(s, pattern):
    need = Counter(pattern)
    best = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            window = Counter(s[i:j])
            if all(window[ch] >= count for ch, count in need.items()):
                if best == 0 or j - i < best:
                    best = j - i
                break
    return best
