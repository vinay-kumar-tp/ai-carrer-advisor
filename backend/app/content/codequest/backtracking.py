"""Backtracking and exhaustive search with pruning."""

from __future__ import annotations

import random
from itertools import permutations

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_STR_LIST,
    P,
    Param,
    STR,
    ints,
    p_int,
    p_nums,
    word,
)

T = ["Backtracking"]
BT = ["Backtracking / Pruning"]
SUB = ["Subsets / Backtracking"]


def specs():
    out: list = []
    add = out.append

    add(P(
        "count-all-subsets", "Count Subsets", "easy", T + ["Arrays"], SUB,
        "Print the number of subsets of `nums`, including the empty one.",
        [p_nums()], OUT_INT, lambda nums: 2 ** len(nums),
        [([1, 2, 3],), ([5],)],
        lambda rng: [(ints(rng, n, 1, 20),) for n in (1, 2, 3, 5, 9, 14, 20, 30)],
        ["1 <= n <= 60", "the answer fits in a 64-bit signed integer"],
        ["Each element is either in or out, independently.",
         "So the count is 2 raised to the number of elements.",
         "Duplicated values still create distinct subsets because positions differ."],
        explanations=["2^3 = 8.", "2^1 = 2."],
    ))

    add(P(
        "generate-subsets-sorted", "Generate All Subsets", "medium", T + ["Arrays"], SUB,
        "Print every subset of `nums`, one per line, as its elements in ascending order separated by "
        "spaces. Print subsets ordered by size, then lexicographically by their sorted contents. The empty "
        "subset is printed as an empty line.",
        [Param("nums", INT_LIST, "distinct integers")], OUT_STR_LIST,
        lambda nums: _all_subsets(nums),
        [([1, 2, 3],), ([7],)],
        lambda rng: [(rng.sample(range(1, 30), n),) for n in (1, 2, 3, 4, 5, 6, 8, 10)],
        ["1 <= n <= 12", "all values are distinct"],
        ["Recurse element by element, choosing to include or exclude each.",
         "Or enumerate bitmasks from 0 to 2^n - 1 and read the set bits.",
         "Sort each subset, then sort the whole collection by (size, contents) for the required order.",
         "The empty subset is a valid line containing nothing."],
        explanations=["8 subsets from the empty one upwards.", "The empty subset and {7}."],
    ))

    add(P(
        "count-permutations", "Count Permutations", "easy", T + ["Math"], BT,
        "Print the number of distinct orderings of the elements of `nums`, accounting for repeated values.",
        [p_nums()], OUT_INT, lambda nums: _count_distinct_permutations(nums),
        [([1, 2, 3],), ([1, 1],)],
        lambda rng: [(ints(rng, n, 1, 4),) for n in (1, 2, 3, 4, 5, 6, 8, 10)],
        ["1 <= n <= 12"],
        ["Without repeats the answer is n factorial.",
         "Repeated values divide out: n! divided by the product of each value's count factorial.",
         "Generating and deduplicating also works at these limits."],
        explanations=["3! = 6.", "The two 1s are interchangeable, giving 1."],
        brute=lambda nums: len(set(permutations(nums))),
    ))

    add(P(
        "generate-permutations-sorted", "Generate All Permutations", "medium", T, BT,
        "Print every distinct permutation of `nums`, one per line as space-separated values, in "
        "lexicographic order.",
        [Param("nums", INT_LIST, "the values to permute")], OUT_STR_LIST,
        lambda nums: [" ".join(map(str, perm)) for perm in sorted(set(permutations(sorted(nums))))],
        [([1, 2, 3],), ([2, 1],)],
        lambda rng: [(ints(rng, n, 1, 3),) for n in (1, 2, 3, 4, 5, 6)],
        ["1 <= n <= 7"],
        ["Sort first, then build permutations by choosing an unused element at each depth.",
         "Skip a candidate equal to the previous one at the same depth to avoid duplicates.",
         "Choosing in sorted order produces lexicographic output naturally."],
        explanations=["Six permutations in order.", "1 2 then 2 1."],
    ))

    add(P(
        "n-queens-solution-count", "N Queens", "hard", T, BT,
        "Print the number of ways to place `n` queens on an `n x n` board so no two attack each other.",
        [p_int("n", "board size")], OUT_INT, lambda n: _n_queens(n),
        [(4,), (1,)],
        lambda rng: [(rng.randint(1, 9),) for _ in range(8)],
        ["1 <= n <= 11"],
        ["Place one queen per row, trying each column.",
         "Track used columns and both diagonal directions in sets for O(1) conflict checks.",
         "The diagonals are identified by row+col and row-col.",
         "Backtrack as soon as a placement conflicts — that pruning is what makes it feasible."],
        explanations=["Two arrangements exist for 4 queens.", "One queen on one square."],
    ))

    add(P(
        "rat-in-maze-path-count", "Count Maze Paths", "medium", T + ["Matrix"], BT,
        "In the grid `g`, `1` marks an open cell and `0` a wall. Starting at the top-left and moving only "
        "down or right through open cells, print how many paths reach the bottom-right.",
        [Param("g", "grid", "rows of 0/1 characters")], OUT_INT,
        lambda g: _maze_paths(g),
        (["111", "101", "111"],) and [(["111", "101", "111"],), (["0"],)],
        lambda rng: [([("".join("1" if rng.random() < 0.75 else "0" for _ in range(c))) for _ in range(r)],)
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (4, 4), (5, 6), (7, 7))],
        ["1 <= r, c <= 12", "each character is 0 or 1",
         "the answer fits in a 64-bit signed integer"],
        ["Recurse from each cell into the down and right neighbours.",
         "Return 0 for a wall or an out-of-bounds cell, and 1 when you land on the target.",
         "Memoising by cell turns the exponential search into O(r*c).",
         "A blocked start or finish yields 0."],
        explanations=["Two paths avoid the central wall.", "The start is a wall."],
    ))

    add(P(
        "combination-sum-count", "Combination Sum Count", "medium", T + ["Arrays"], BT,
        "Using the distinct positive values of `candidates` any number of times, print how many "
        "combinations sum to `target`. Two combinations differ only by their multiset of values.",
        [Param("candidates", INT_LIST, "distinct positive integers"), p_int("target", "the required sum")],
        OUT_INT, lambda candidates, target: _combination_sum_count(candidates, target),
        [([2, 3, 6, 7], 7), ([5], 3)],
        lambda rng: [(rng.sample(range(1, 12), rng.randint(1, 4)), rng.randint(0, 40)) for _ in range(8)],
        ["1 <= number of candidates <= 20", "1 <= candidates[i] <= 100", "0 <= target <= 500"],
        ["Recurse with an index so you never step backwards, which prevents reordered duplicates.",
         "At each step either reuse the current candidate or move to the next one.",
         "Prune as soon as the running sum exceeds the target.",
         "target = 0 has exactly one combination: the empty one."],
        explanations=["7 and 2+2+3 give 2.", "3 cannot be made from 5."],
    ))

    add(P(
        "subset-sum-count-distinct-values", "Count Subsets With Given Sum", "medium",
        T + ["Dynamic Programming"], SUB,
        "Print how many subsets of `nums` sum to exactly `target`. Subsets at different index sets count "
        "separately.",
        [Param("nums", INT_LIST, "non-negative integers"), p_int("target")], OUT_INT,
        lambda nums, target: _count_subsets_sum(nums, target),
        [([1, 2, 3, 3], 6), ([1, 1], 5)],
        lambda rng: [(ints(rng, n, 0, 8), rng.randint(0, 25)) for n in (1, 2, 3, 5, 9, 14, 18)],
        ["1 <= n <= 20", "0 <= nums[i] <= 100", "0 <= target <= 2000"],
        ["Full enumeration over 2^n masks is fine for n up to 20.",
         "A subset-sum DP counts them in O(n * target) instead.",
         "Iterate sums downwards so each element is used at most once."],
        explanations=["{3,3} and {1,2,3} twice gives 3.", "The total is only 2."],
        brute=lambda nums, target: sum(
            1 for mask in range(1 << len(nums))
            if sum(nums[i] for i in range(len(nums)) if mask >> i & 1) == target
        ),
    ))

    add(P(
        "palindrome-partition-count", "Count Palindrome Partitions", "hard", T + ["Strings"], BT,
        "Print the number of ways to split `s` so every part is a palindrome.",
        [Param("s", STR, "lowercase letters")], OUT_INT,
        lambda s: _palindrome_partitions(s),
        [("aab",), ("aaa",)],
        lambda rng: [(word(rng, n, "ab"),) for n in (1, 2, 3, 4, 6, 9, 13, 16)],
        ["1 <= |s| <= 20", "s contains lowercase English letters only"],
        ["Try every prefix that is a palindrome, then recurse on the rest.",
         "Precomputing an is-palindrome table removes repeated checks.",
         "The empty remainder counts as one complete partition.",
         "Memoising by start index turns this into a linear DP."],
        explanations=["a|a|b and aa|b give 2.", "Four ways split aaa."],
    ))

    add(P(
        "letter-case-permutation-count", "Letter Case Permutations", "easy", T + ["Strings"], BT,
        "The string `s` mixes lowercase letters and digits. Each letter may stay lowercase or become "
        "uppercase. Print how many distinct strings can be produced.",
        [Param("s", STR, "lowercase letters and digits")], OUT_INT,
        lambda s: 2 ** sum(1 for ch in s if ch.isalpha()),
        [("a1b2",), ("123",)],
        lambda rng: [("".join(rng.choice("ab12") for _ in range(n)),) for n in (1, 2, 3, 5, 8, 12, 20, 40)],
        ["1 <= |s| <= 60", "the answer fits in a 64-bit signed integer"],
        ["Only letters offer a choice; digits are fixed.",
         "So the answer is 2 raised to the number of letters.",
         "A string of only digits gives 1."],
        explanations=["Two letters give 4.", "No letters, so only the original."],
    ))

    add(P(
        "sudoku-row-valid-count", "Count Valid Placements", "medium", T + ["Matrix"], BT,
        "The `n x n` matrix `board` uses `0` for an empty cell. Print how many values from `1..n` could "
        "legally go into the first empty cell without repeating a value in its row or column. Print `0` if "
        "there is no empty cell.",
        [Param("board", "int[][]", "a square board, 0 marks empty"), p_int("n", "the value range")],
        OUT_INT, lambda board, n: _valid_placements(board, n),
        [([[1, 0], [0, 2]], 2), ([[1, 2], [2, 1]], 2)],
        lambda rng: [(lambda size: ([[rng.choice([0, rng.randint(1, size)]) for _ in range(size)]
                                     for _ in range(size)], size))(size)
                     for size in (1, 2, 2, 3, 4, 5, 6, 8)],
        ["1 <= n <= 20", "board is n x n", "0 <= board[i][j] <= n"],
        ["Scan row by row for the first zero.",
         "Collect the values already used in that cell's row and column.",
         "Count how many of 1..n remain available.",
         "This candidate count is exactly what a Sudoku solver computes before recursing."],
        explanations=["Only 2 fits at (0,1).", "The board is full."],
    ))

    add(P(
        "word-search-exists-grid", "Word Search", "medium", T + ["Matrix", "Strings"], BT,
        "Print `YES` if `wordToFind` can be spelled by moving between orthogonally adjacent cells of the "
        "grid `g` without reusing a cell, else `NO`.",
        [Param("g", "grid", "rows of lowercase letters"),
         Param("wordToFind", STR, "the word to spell")], OUT_BOOL,
        lambda g, wordToFind: _word_search(g, wordToFind),
        ([["abc", "def"], "abc"],) and [(["abc", "def"], "abc"), (["abc", "def"], "az")],
        lambda rng: [(lambda r, c: ([word(rng, c, "ab") for _ in range(r)],
                                    word(rng, rng.randint(1, 4), "ab")))(r, c)
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (4, 4), (5, 5), (6, 6))],
        ["1 <= r, c <= 8", "1 <= |wordToFind| <= 12", "lowercase English letters only"],
        ["Try every cell as a starting point.",
         "Recurse into the four neighbours, marking cells visited on the way in and unmarking on the way out.",
         "That unmarking is the backtracking step — forgetting it blocks valid paths.",
         "Prune immediately when the current character does not match."],
        explanations=["a-b-c runs along the top row.", "There is no z in the grid."],
    ))

    add(P(
        "generate-balanced-parentheses-count", "Count Balanced Parentheses", "medium", T + ["Strings"], BT,
        "Print how many distinct balanced parentheses strings use exactly `n` pairs.",
        [p_int("n", "number of pairs")], OUT_INT, lambda n: _catalan(n),
        [(3,), (1,)],
        lambda rng: [(rng.randint(0, 16),) for _ in range(8)],
        ["0 <= n <= 18", "the answer fits in a 64-bit signed integer"],
        ["Build strings by adding '(' while any remain, and ')' only while it would stay balanced.",
         "The count is the n-th Catalan number.",
         "n = 0 has exactly one string: the empty one."],
        explanations=["((())), (()()), (())(), ()(()) and ()()() give 5.", "Only ()."],
        brute=lambda n: _count_balanced_brute(n),
    ))

    add(P(
        "knight-tour-reachable-count", "Knight Moves Reachable", "medium", T + ["Matrix"], BT,
        "From cell `(0, 0)` of an `n x n` board, print how many distinct cells a knight can reach in at "
        "most `k` moves, counting the starting cell.",
        [p_int("n", "board size"), p_int("k", "move budget")], OUT_INT,
        lambda n, k: _knight_reachable(n, k),
        [(3, 1), (1, 5)],
        lambda rng: [(rng.randint(1, 8), rng.randint(0, 4)) for _ in range(8)],
        ["1 <= n <= 8", "0 <= k <= 6"],
        ["A knight has eight candidate moves; filter the ones leaving the board.",
         "BFS layer by layer up to depth k and collect the visited cells.",
         "Depth-limited DFS also works but revisits cells unless you memoise by (cell, remaining).",
         "k = 0 means only the start is reachable."],
        explanations=["The start plus two knight destinations gives 3.", "A 1x1 board."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _all_subsets(nums):
    values = sorted(nums)
    collected = []
    for mask in range(1 << len(values)):
        subset = [values[i] for i in range(len(values)) if mask >> i & 1]
        collected.append(subset)
    collected.sort(key=lambda subset: (len(subset), subset))
    return [" ".join(map(str, subset)) for subset in collected]


def _count_distinct_permutations(nums):
    from collections import Counter
    from math import factorial

    total = factorial(len(nums))
    for count in Counter(nums).values():
        total //= factorial(count)
    return total


def _n_queens(n):
    columns: set[int] = set()
    diag1: set[int] = set()
    diag2: set[int] = set()
    count = 0

    def place(row):
        nonlocal count
        if row == n:
            count += 1
            return
        for column in range(n):
            if column in columns or (row + column) in diag1 or (row - column) in diag2:
                continue
            columns.add(column)
            diag1.add(row + column)
            diag2.add(row - column)
            place(row + 1)
            columns.discard(column)
            diag1.discard(row + column)
            diag2.discard(row - column)

    place(0)
    return count


def _maze_paths(g):
    rows, cols = len(g), len(g[0])
    if g[0][0] == "0" or g[rows - 1][cols - 1] == "0":
        return 0
    memo: dict[tuple[int, int], int] = {}

    def walk(r, c):
        if r >= rows or c >= cols or g[r][c] == "0":
            return 0
        if (r, c) == (rows - 1, cols - 1):
            return 1
        if (r, c) in memo:
            return memo[(r, c)]
        memo[(r, c)] = walk(r + 1, c) + walk(r, c + 1)
        return memo[(r, c)]

    return walk(0, 0)


def _combination_sum_count(candidates, target):
    values = sorted(candidates)

    def count(index, remaining):
        if remaining == 0:
            return 1
        if index >= len(values) or remaining < 0:
            return 0
        return count(index, remaining - values[index]) + count(index + 1, remaining)

    return count(0, target)


def _count_subsets_sum(nums, target):
    counts = {0: 1}
    for value in nums:
        updated = dict(counts)
        for total, ways in counts.items():
            new_total = total + value
            if new_total <= target:
                updated[new_total] = updated.get(new_total, 0) + ways
        counts = updated
    return counts.get(target, 0)


def _palindrome_partitions(s):
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for right in range(n):
        for left in range(right, -1, -1):
            if s[left] == s[right] and (right - left < 2 or is_pal[left + 1][right - 1]):
                is_pal[left][right] = True

    memo: dict[int, int] = {}

    def count(start):
        if start == n:
            return 1
        if start in memo:
            return memo[start]
        total = 0
        for end in range(start, n):
            if is_pal[start][end]:
                total += count(end + 1)
        memo[start] = total
        return total

    return count(0)


def _valid_placements(board, n):
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == 0:
                used = {board[r][cc] for cc in range(len(board[0]))}
                used |= {board[rr][c] for rr in range(len(board))}
                return sum(1 for value in range(1, n + 1) if value not in used)
    return 0


def _word_search(g, wordToFind):
    rows, cols = len(g), len(g[0])
    visited = [[False] * cols for _ in range(rows)]

    def search(r, c, index):
        if index == len(wordToFind):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or visited[r][c] or g[r][c] != wordToFind[index]:
            return False
        visited[r][c] = True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if search(r + dr, c + dc, index + 1):
                visited[r][c] = False
                return True
        if index == len(wordToFind) - 1:
            visited[r][c] = False
            return True
        visited[r][c] = False
        return False

    for r in range(rows):
        for c in range(cols):
            if search(r, c, 0):
                return True
    return False


def _catalan(n):
    table = [0] * (n + 1)
    table[0] = 1
    for i in range(1, n + 1):
        table[i] = sum(table[j] * table[i - 1 - j] for j in range(i))
    return table[n]


def _count_balanced_brute(n):
    total = 0

    def build(open_used, close_used):
        nonlocal total
        if open_used == n and close_used == n:
            total += 1
            return
        if open_used < n:
            build(open_used + 1, close_used)
        if close_used < open_used:
            build(open_used, close_used + 1)

    build(0, 0)
    return total


KNIGHT_MOVES = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))


def _knight_reachable(n, k):
    from collections import deque

    seen = {(0, 0)}
    queue = deque([(0, 0, 0)])
    while queue:
        r, c, depth = queue.popleft()
        if depth == k:
            continue
        for dr, dc in KNIGHT_MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append((nr, nc, depth + 1))
    return len(seen)
