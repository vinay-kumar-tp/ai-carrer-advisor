"""Combinatorial game theory."""

from __future__ import annotations

import random
from math import gcd

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    P,
    Param,
    ints,
    p_int,
    p_nums,
)

T = ["Game Theory"]
GT = ["Game Theory"]

FIRST_WINS = "Print `YES` if the first player wins with optimal play from both sides, else `NO`."


def specs():
    out: list = []
    add = out.append

    add(P(
        "nim-game-single-pile", "Nim Single Pile", "easy", T, GT,
        "A pile holds `n` stones. Players alternate removing 1, 2 or 3 stones and whoever takes the last "
        "stone wins. " + FIRST_WINS,
        [p_int("n", "stones in the pile")], OUT_BOOL, lambda n: n % 4 != 0,
        [(4,), (5,)],
        lambda rng: [(rng.randint(0, 10 ** 6),) for _ in range(8)],
        ["0 <= n <= 10^9"],
        ["Positions that are multiples of 4 are losing for the player to move.",
         "From any other count you can move to a multiple of 4 and hand the loss over.",
         "So the test is simply n mod 4 being non-zero.",
         "n = 0 means the first player already lost."],
        explanations=["4 is a multiple of 4, so the first player loses.",
                      "Taking 1 leaves 4 for the opponent."],
        brute=lambda n: _win_subtract(n, (1, 2, 3)) if n <= 3000 else n % 4 != 0,
    ))

    add(P(
        "nim-game-xor", "Nim With Multiple Piles", "medium", T + ["Bit Manipulation"], GT,
        "Several piles hold the given numbers of stones. A move removes any positive number of stones from "
        "one pile, and whoever takes the last stone wins. " + FIRST_WINS,
        [Param("piles", INT_LIST, "stones in each pile")], OUT_BOOL,
        lambda piles: _xor(piles) != 0,
        [([1, 2, 3],), ([1, 1],)],
        lambda rng: [(ints(rng, n, 0, 40),) for n in (1, 2, 3, 5, 9, 18, 45, 120)],
        ["1 <= n <= 2000", "0 <= piles[i] <= 10^9"],
        ["The Sprague-Grundy value of a Nim position is the XOR of the pile sizes.",
         "A position is losing exactly when that XOR is 0.",
         "From a non-zero XOR you can always move to a zero one.",
         "This is the single most reused result in impartial game theory."],
        explanations=["1 XOR 2 XOR 3 = 0, so the first player loses.",
                      "1 XOR 1 = 0, so the first player loses."],
    ))

    add(P(
        "stone-game-take-one-or-two", "Take One Or Two", "easy", T, GT,
        "A pile holds `n` stones. Players alternate removing 1 or 2 stones and whoever takes the last stone "
        "wins. " + FIRST_WINS,
        [p_int("n", "stones in the pile")], OUT_BOOL, lambda n: n % 3 != 0,
        [(3,), (4,)],
        lambda rng: [(rng.randint(0, 10 ** 6),) for _ in range(8)],
        ["0 <= n <= 10^9"],
        ["Multiples of 3 are losing positions.",
         "Whatever the first player takes, the opponent restores the multiple of 3.",
         "Generalising: with moves 1..k the losing positions are multiples of k+1."],
        explanations=["3 is a multiple of 3.", "Taking 1 leaves 3."],
        brute=lambda n: _win_subtract(n, (1, 2)) if n <= 3000 else n % 3 != 0,
    ))

    add(P(
        "subtraction-game-custom-moves", "Subtraction Game", "medium", T + ["Dynamic Programming"], GT,
        "A pile holds `n` stones. A move removes exactly one of the amounts listed in `moves`, and the "
        "player unable to move loses. " + FIRST_WINS,
        [p_int("n", "stones in the pile"), Param("moves", INT_LIST, "the allowed removals")], OUT_BOOL,
        lambda n, moves: _win_subtract(n, tuple(moves)),
        [(5, [1, 3]), (4, [2])],
        lambda rng: [(rng.randint(0, 400), rng.sample(range(1, 10), rng.randint(1, 4))) for _ in range(8)],
        ["0 <= n <= 2000", "1 <= number of moves <= 10", "1 <= moves[i] <= 100"],
        ["Compute win/lose for every count from 0 upwards.",
         "A position wins when some legal move leads to a losing position.",
         "Position 0 is a loss for the player to move.",
         "This bottom-up DP is O(n * |moves|)."],
        explanations=["Removing 1 leaves 4, which is losing for the opponent.",
                      "Removing 2 leaves 2, from which the opponent removes 2 and wins."],
    ))

    add(P(
        "stone-game-optimal-difference", "Optimal Score Difference", "medium",
        T + ["Dynamic Programming"], GT,
        "The `stones` sit in a row. Players alternate taking either end, adding its value to their score. "
        "Print the first player's score minus the second player's score with optimal play from both.",
        [Param("stones", INT_LIST, "the row of values")], OUT_INT,
        lambda stones: _optimal_difference(stones),
        [([5, 3, 4, 5],), ([7],)],
        lambda rng: [(ints(rng, n, -20, 40),) for n in (1, 2, 3, 5, 9, 16, 35, 80)],
        ["1 <= n <= 500", "-10^4 <= stones[i] <= 10^4"],
        ["dp[i][j] is the best achievable difference on the subarray from i to j.",
         "Taking the left end gives stones[i] - dp[i+1][j]; the right end gives stones[j] - dp[i][j-1].",
         "The subtraction encodes the turn swap — the opponent's advantage becomes your deficit.",
         "Solve by increasing subarray length."],
        explanations=["The first player can guarantee a lead of 1.", "One stone."],
    ))

    add(P(
        "can-first-player-win-row-game", "Row Game Winner", "medium", T + ["Dynamic Programming"], GT,
        "The `stones` sit in a row. Players alternate taking either end, adding its value to their score. "
        + FIRST_WINS + " A tie counts as a loss for the first player.",
        [Param("stones", INT_LIST, "the row of values")], OUT_BOOL,
        lambda stones: _optimal_difference(stones) > 0,
        [([1, 5, 2],), ([1, 1],)],
        lambda rng: [(ints(rng, n, 0, 20),) for n in (1, 2, 3, 5, 9, 16, 35, 80)],
        ["1 <= n <= 500", "0 <= stones[i] <= 10^4"],
        ["Compute the optimal score difference, then test whether it is positive.",
         "A difference of exactly 0 is a tie, which the rules call a loss here.",
         "The DP is the same one used for the difference itself."],
        explanations=["The best the first player can force is a deficit.", "Both players score 1."],
    ))

    add(P(
        "divisor-game-win", "Divisor Game", "easy", T, GT,
        "A number `n` is on the board. A move replaces `n` with `n - d` for some divisor `d` of `n` with "
        "`0 < d < n`. The player unable to move loses. " + FIRST_WINS,
        [p_int("n", "the starting number")], OUT_BOOL, lambda n: n % 2 == 0,
        [(2,), (3,)],
        lambda rng: [(rng.randint(1, 10 ** 6),) for _ in range(8)],
        ["1 <= n <= 10^9"],
        ["Even numbers win and odd numbers lose.",
         "From an even number you can always subtract 1 to hand over an odd one.",
         "Every divisor of an odd number is odd, so an odd number can only produce an even one.",
         "n = 1 offers no move and therefore loses."],
        explanations=["Subtracting 1 leaves 1 with no move.", "Any move from 3 leaves an even number."],
        brute=lambda n: _divisor_game_dp(n) if n <= 2000 else n % 2 == 0,
    ))

    add(P(
        "coin-pile-game-grundy", "Grundy Value Of Pile", "hard", T, GT,
        "A pile holds `n` stones and a move removes exactly one of the amounts in `moves`. Print the Grundy "
        "value of the position.",
        [p_int("n", "stones in the pile"), Param("moves", INT_LIST, "the allowed removals")], OUT_INT,
        lambda n, moves: _grundy(n, tuple(moves)),
        [(5, [1, 2]), (0, [1])],
        lambda rng: [(rng.randint(0, 300), rng.sample(range(1, 8), rng.randint(1, 4))) for _ in range(8)],
        ["0 <= n <= 2000", "1 <= number of moves <= 10", "1 <= moves[i] <= 100"],
        ["The Grundy value is the smallest non-negative integer missing from the set of reachable "
         "positions' Grundy values.",
         "That is the minimum excludant, or mex.",
         "Grundy 0 marks a losing position, which is why XOR of Grundy values decides sums of games.",
         "Compute values bottom-up from 0."],
        explanations=["Reachable Grundy values are {1,0}, so the mex is 2.", "No move gives Grundy 0."],
    ))

    add(P(
        "two-pile-game-equal-win", "Two Pile Removal Game", "medium", T, GT,
        "Two piles hold `a` and `b` stones. A move removes any positive number from one pile, or the same "
        "positive number from both. The player unable to move loses. " + FIRST_WINS,
        [p_int("a", "first pile"), p_int("b", "second pile")], OUT_BOOL,
        lambda a, b: _wythoff_win(a, b),
        [(1, 2), (2, 3)],
        # Kept small on purpose: the cross-check DP is O(a*b*max(a,b)).
        lambda rng: [(rng.randint(0, 40), rng.randint(0, 40)) for _ in range(8)],
        ["0 <= a, b <= 2000"],
        ["This is Wythoff's game; its losing positions are the golden-ratio pairs.",
         "The k-th losing pair is (floor(k*phi), floor(k*phi^2)) for k = 0, 1, 2, ...",
         "A bottom-up DP over both pile sizes is easier to get exactly right.",
         "(0,0) is losing for the player to move."],
        explanations=["(1,2) is a losing pair, so the first player loses.",
                      "From (2,3) you can move to (1,2)."],
        brute=lambda a, b: _wythoff_dp(a, b),
    ))

    add(P(
        "misere-nim-single-pile", "Last Stone Loses", "easy", T, GT,
        "A pile holds `n` stones. Players alternate removing 1, 2 or 3 stones and whoever takes the **last** "
        "stone **loses**. " + FIRST_WINS,
        [p_int("n", "stones in the pile")], OUT_BOOL, lambda n: n % 4 != 1,
        [(1,), (2,)],
        lambda rng: [(rng.randint(1, 10 ** 6),) for _ in range(8)],
        ["1 <= n <= 10^9"],
        ["In the misere version you want to leave exactly 1 stone for the opponent.",
         "So positions with n mod 4 == 1 are losing.",
         "The winning move always restores that residue.",
         "n = 1 forces you to take the last stone and lose."],
        explanations=["Only one stone remains and you must take it.",
                      "Take 1 and leave a single stone."],
        brute=lambda n: _misere_dp(n) if n <= 3000 else n % 4 != 1,
    ))

    add(P(
        "game-of-stones-two-players-array", "Pick From Ends Maximum Score", "medium",
        T + ["Dynamic Programming"], GT,
        "The `stones` sit in a row and players alternate taking either end. Print the maximum score the "
        "first player can guarantee.",
        [Param("stones", INT_LIST, "non-negative values")], OUT_INT,
        lambda stones: (sum(stones) + _optimal_difference(stones)) // 2,
        [([5, 3, 7, 10],), ([4],)],
        lambda rng: [(ints(rng, n, 0, 30),) for n in (1, 2, 3, 5, 9, 16, 35, 80)],
        ["1 <= n <= 500", "0 <= stones[i] <= 10^4"],
        ["Compute the optimal difference d and the total t.",
         "The first player's score is (t + d) / 2 because the two scores sum to t and differ by d.",
         "The sum and difference are always the same parity, so the division is exact."],
        explanations=["The first player can secure 15.", "The single stone."],
    ))

    add(P(
        "matchstick-game-modulo", "Matchstick Game", "easy", T, GT,
        "A pile holds `n` matchsticks. A move removes between 1 and `k` sticks and whoever takes the last "
        "one wins. " + FIRST_WINS,
        [p_int("n", "matchsticks in the pile"), p_int("k", "maximum removal")], OUT_BOOL,
        lambda n, k: n % (k + 1) != 0,
        [(10, 3), (8, 3)],
        lambda rng: [(rng.randint(0, 10 ** 6), rng.randint(1, 20)) for _ in range(8)],
        ["0 <= n <= 10^9", "1 <= k <= 10^6"],
        ["Losing positions are the multiples of k+1.",
         "Whatever you remove, the opponent removes the complement to k+1.",
         "So the answer is n mod (k+1) being non-zero.",
         "k = 3 gives the familiar multiples-of-4 rule."],
        explanations=["10 mod 4 is 2, so the first player wins.", "8 is a multiple of 4."],
        brute=lambda n, k: _win_subtract(n, tuple(range(1, k + 1))) if n <= 2000 and k <= 50
        else n % (k + 1) != 0,
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def _win_subtract(n, moves):
    win = [False] * (n + 1)
    for count in range(1, n + 1):
        win[count] = any(count - move >= 0 and not win[count - move] for move in moves)
    return win[n]


def _optimal_difference(stones):
    n = len(stones)
    dp = [[0] * n for _ in range(n)]
    for index in range(n):
        dp[index][index] = stones[index]
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            dp[left][right] = max(stones[left] - dp[left + 1][right],
                                  stones[right] - dp[left][right - 1])
    return dp[0][n - 1]


def _divisor_game_dp(n):
    win = [False] * (n + 1)
    for value in range(2, n + 1):
        for divisor in range(1, value):
            if value % divisor == 0 and not win[value - divisor]:
                win[value] = True
                break
    return win[n]


def _grundy(n, moves):
    values = [0] * (n + 1)
    for count in range(1, n + 1):
        reachable = {values[count - move] for move in moves if count - move >= 0}
        mex = 0
        while mex in reachable:
            mex += 1
        values[count] = mex
    return values[n]


def _wythoff_dp(a, b):
    limit_a, limit_b = a, b
    win = [[False] * (limit_b + 1) for _ in range(limit_a + 1)]
    for x in range(limit_a + 1):
        for y in range(limit_b + 1):
            if x == 0 and y == 0:
                win[x][y] = False
                continue
            found = False
            for take in range(1, x + 1):
                if not win[x - take][y]:
                    found = True
                    break
            if not found:
                for take in range(1, y + 1):
                    if not win[x][y - take]:
                        found = True
                        break
            if not found:
                for take in range(1, min(x, y) + 1):
                    if not win[x - take][y - take]:
                        found = True
                        break
            win[x][y] = found
    return win[a][b]


def _wythoff_win(a, b):
    low, high = min(a, b), max(a, b)
    difference = high - low
    # The k-th cold position has low = floor(k * phi); phi = (1 + sqrt(5)) / 2.
    phi = (1 + 5 ** 0.5) / 2
    expected_low = int(difference * phi)
    return low != expected_low


def _misere_dp(n):
    """Taking the last stone loses, so position 1 is a loss for the player to move."""
    win = [False] * (n + 1)
    for count in range(2, n + 1):
        win[count] = any(count - move >= 1 and not win[count - move] for move in (1, 2, 3))
    return win[n]
