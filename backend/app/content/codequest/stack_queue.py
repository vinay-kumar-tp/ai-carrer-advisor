"""Stack, queue and monotonic-structure problems."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR,
    P,
    Param,
    STR,
    ints,
    p_int,
    p_nums,
    word,
)

T = ["Stack & Queue"]
SQ = ["Stack / Queue"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)


def g_nums(lo=-40, hi=40, sizes=SIZES):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "next-greater-element", "Next Greater Element", "medium", T + ["Arrays"], SQ,
        "For each position of `nums`, print the first value to its right that is strictly greater, or "
        "`-1` if none exists. Print the answers space separated.",
        [p_nums()], OUT_INT_LIST, lambda nums: _next_greater(nums),
        [([4, 5, 2, 25],), ([3, 2, 1],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sweep from right to left keeping a stack of candidate values.",
         "Pop everything not greater than the current element — those can never be an answer again.",
         "The stack top is then the next greater element, or the stack is empty for -1.",
         "Each element is pushed and popped once, giving O(n)."],
        explanations=["5, 25, 25 and then -1.", "The array decreases, so every answer is -1."],
        brute=lambda nums: [next((nums[j] for j in range(i + 1, len(nums)) if nums[j] > nums[i]), -1)
                            for i in range(len(nums))],
        pattern_note="A monotonic stack keeps only elements that could still be an answer. Anything "
                     "dominated by a newer element is discarded permanently, so total work stays linear.",
    ))

    add(P(
        "next-smaller-element", "Next Smaller Element", "medium", T + ["Arrays"], SQ,
        "For each position of `nums`, print the first value to its right that is strictly smaller, or "
        "`-1` if none exists.",
        [p_nums()], OUT_INT_LIST, lambda nums: _next_smaller(nums),
        [([4, 5, 2, 25],), ([1, 2, 3],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Mirror the next-greater sweep but keep an increasing stack.",
         "Pop values that are not smaller than the current element.",
         "Sweeping right to left keeps the logic simple."],
        brute=lambda nums: [next((nums[j] for j in range(i + 1, len(nums)) if nums[j] < nums[i]), -1)
                            for i in range(len(nums))],
    ))

    add(P(
        "previous-greater-element", "Previous Greater Element", "medium", T + ["Arrays"], SQ,
        "For each position of `nums`, print the nearest value to its left that is strictly greater, or "
        "`-1` if none exists.",
        [p_nums()], OUT_INT_LIST, lambda nums: _previous_greater(nums),
        [([4, 5, 2, 25],), ([5, 4, 3],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sweep left to right with a decreasing stack.",
         "Pop values not greater than the current element before reading the top.",
         "Push the current element after answering for it."],
        brute=lambda nums: [next((nums[j] for j in range(i - 1, -1, -1) if nums[j] > nums[i]), -1)
                            for i in range(len(nums))],
    ))

    add(P(
        "previous-smaller-element", "Previous Smaller Element", "medium", T + ["Arrays"], SQ,
        "For each position of `nums`, print the nearest value to its left that is strictly smaller, or "
        "`-1` if none exists.",
        [p_nums()], OUT_INT_LIST, lambda nums: _previous_smaller(nums),
        [([4, 5, 2, 25],), ([3, 4, 5],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sweep left to right with an increasing stack.",
         "Pop values that are not smaller than the current element.",
         "This is the building block for the largest-rectangle problem."],
        brute=lambda nums: [next((nums[j] for j in range(i - 1, -1, -1) if nums[j] < nums[i]), -1)
                            for i in range(len(nums))],
    ))

    add(P(
        "next-greater-circular", "Next Greater Element Circular", "medium", T + ["Arrays"], SQ,
        "The array `nums` is circular. For each position print the first strictly greater value found by "
        "walking right and wrapping around, or `-1` if none exists.",
        [p_nums()], OUT_INT_LIST, lambda nums: _next_greater_circular(nums),
        [([1, 2, 1],), ([5, 5],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Run the monotonic stack sweep over two concatenated copies of the array.",
         "Only record answers for the first copy's indices.",
         "Equal values do not count as greater, so a constant array answers all -1."],
        explanations=["2, -1, 2 after wrapping.", "No value is strictly greater."],
        brute=lambda nums: [next((nums[(i + step) % len(nums)] for step in range(1, len(nums))
                                  if nums[(i + step) % len(nums)] > nums[i]), -1)
                            for i in range(len(nums))],
    ))

    add(P(
        "stock-span-values", "Stock Span", "medium", T + ["Arrays"], SQ,
        "For each position `i` of `nums`, print how many consecutive positions ending at `i` (including "
        "`i`) have values less than or equal to `nums[i]`.",
        [p_nums()], OUT_INT_LIST, lambda nums: _stock_span(nums),
        [([100, 80, 60, 70, 60, 75, 85],), ([1, 2],)], g_nums(0, 40),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["The span ends where the previous strictly greater element sits.",
         "Keep a decreasing stack of indices and pop while the top value is <= the current one.",
         "The span is i minus the index left on the stack, or i+1 when the stack empties."],
        explanations=["Spans are 1,1,1,2,1,4,6.", "Spans are 1 and 2."],
        brute=lambda nums: [_span_brute(nums, i) for i in range(len(nums))],
    ))

    add(P(
        "largest-rectangle-histogram", "Largest Rectangle In Histogram", "hard", T + ["Arrays"], SQ,
        "Each `heights[i]` is a bar of width 1. Print the area of the largest axis-aligned rectangle that "
        "fits inside the histogram.",
        [Param("heights", INT_LIST, "non-negative bar heights")], OUT_INT,
        lambda heights: _largest_rectangle(heights),
        [([2, 1, 5, 6, 2, 3],), ([4],)],
        lambda rng: [(ints(rng, n, 0, 25),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= heights[i] <= 10^4",
         "the answer fits in a 64-bit signed integer"],
        ["For each bar, the widest rectangle of that height stretches to the nearest smaller bar on "
         "each side.",
         "A monotonic increasing stack of indices finds both boundaries in one pass.",
         "When you pop a bar, the popped height times the span between the new top and the current index "
         "is a candidate area.",
         "Appending a sentinel height of 0 flushes the stack at the end."],
        explanations=["Bars 5 and 6 give 2 * 5 = 10.", "A single bar of height 4."],
        brute=lambda heights: max(min(heights[i:j]) * (j - i)
                                  for i in range(len(heights)) for j in range(i + 1, len(heights) + 1)),
    ))

    add(P(
        "max-area-binary-matrix-rows", "Maximum Rectangle Of Ones", "hard",
        T + ["Matrix", "Dynamic Programming"], SQ,
        "The grid `g` holds `0` and `1` characters. Print the area of the largest rectangle consisting "
        "only of `1`s.",
        [Param("g", "grid", "rows of 0/1 characters")], OUT_INT,
        lambda g: _max_rectangle(g),
        [(["10100", "10111", "11111", "10010"],), (["0"],)],
        lambda rng: [([("".join("1" if rng.random() < 0.6 else "0" for _ in range(c))) for _ in range(r)],)
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (5, 5), (8, 7), (12, 10))],
        ["1 <= r, c <= 200", "each character is 0 or 1"],
        ["Build a histogram per row: the number of consecutive 1s ending at that row in each column.",
         "Then run largest-rectangle-in-histogram on each row's histogram.",
         "The best area across all rows is the answer.",
         "A 0 resets that column's height to 0."],
        explanations=["A 2x3 block of ones gives area 6.", "There are no ones."],
    ))

    add(P(
        "evaluate-postfix-expression", "Evaluate Postfix", "medium", T + ["Strings"], SQ,
        "The array `tokens` encodes a postfix expression: a value at least `-1000` is an operand, while "
        "`-1001`, `-1002`, `-1003` and `-1004` mean add, subtract, multiply and integer-divide "
        "respectively. Print the result. Division truncates toward zero.",
        [Param("tokens", INT_LIST, "operands and operator codes")], OUT_INT,
        lambda tokens: _eval_postfix(tokens),
        [([2, 3, -1001],), ([5, 1, 2, -1001, -1004],)],
        lambda rng: [(_postfix_case(rng, k),) for k in (1, 2, 3, 4, 6, 9, 14)],
        ["1 <= n <= 2000", "operands satisfy -1000 <= value <= 1000",
         "the expression is always valid and never divides by zero"],
        ["Push operands onto a stack.",
         "On an operator, pop two values, apply it with the correct operand order, and push the result.",
         "The second popped value is the left operand.",
         "The stack holds exactly one value at the end."],
        explanations=["2 + 3 = 5.", "5 / (1 + 2) = 1 after truncation."],
    ))

    add(P(
        "min-stack-operations", "Minimum Tracking Stack", "medium", T, SQ,
        "Simulate a stack over the array `ops`: a value at least `0` is pushed, `-1` pops the top, and "
        "`-2` queries the current minimum. Print the answer to every query, space separated. A query on "
        "an empty stack answers `-1`.",
        [Param("ops", INT_LIST, "push values, -1 to pop, -2 to query minimum")], OUT_INT_LIST,
        lambda ops: _min_stack(ops),
        [([5, 3, -2, -1, -2],), ([-2],)],
        lambda rng: [([rng.choice([rng.randint(0, 30), -1, -2, -2]) for _ in range(n)],)
                     for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= n <= 2000", "0 <= push value <= 10^6"],
        ["Keep a second stack holding the minimum at each depth.",
         "On push, store min(newValue, currentMinimum).",
         "On pop, discard the top of both stacks so the minimum rewinds correctly.",
         "That makes every operation O(1)."],
        explanations=["Minimum is 3, then 5 after the pop.", "The stack is empty."],
        brute=lambda ops: _min_stack_brute(ops),
    ))

    add(P(
        "queue-using-two-stacks", "Queue Simulation", "easy", T, SQ,
        "Simulate a FIFO queue over the array `ops`: a value at least `0` is enqueued and `-1` dequeues. "
        "Print each dequeued value in order, space separated. Dequeuing an empty queue yields `-1`.",
        [Param("ops", INT_LIST, "enqueue values, -1 to dequeue")], OUT_INT_LIST,
        lambda ops: _queue_sim(ops),
        [([1, 2, -1, 3, -1],), ([-1],)],
        lambda rng: [([rng.choice([rng.randint(0, 30), -1, -1]) for _ in range(n)],)
                     for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= n <= 2000", "0 <= enqueue value <= 10^6"],
        ["A queue can be built from two stacks: one for input, one for output.",
         "Move everything across only when the output stack empties, giving amortised O(1).",
         "An index-based approach over an array is simpler here."],
        explanations=["Dequeues yield 1 then 2.", "The queue is empty."],
    ))

    add(P(
        "balanced-brackets-single-type", "Balanced Parentheses Depth", "easy", T + ["Strings"], SQ,
        "The string `s` contains only `(` and `)`. Print the maximum nesting depth if the string is "
        "balanced, or `-1` if it is not.",
        [Param("s", STR, "only ( and ) characters")], OUT_INT,
        lambda s: _max_depth(s),
        [("((()))",), (")(",)],
        lambda rng: [("".join(rng.choice("()") for _ in range(n)),) for n in (1, 2, 4, 8, 15, 40, 100, 240)],
        ["1 <= |s| <= 2000", "s contains only ( and )"],
        ["Track a running counter: +1 on '(' and -1 on ')'.",
         "The string is unbalanced if the counter ever goes negative or ends non-zero.",
         "The maximum value the counter reaches is the nesting depth."],
        explanations=["Depth 3.", "The first character closes nothing."],
    ))

    add(P(
        "remove-adjacent-duplicates-stack", "Remove Adjacent Duplicates", "easy", T + ["Strings"], SQ,
        "Repeatedly delete two adjacent equal characters from `s` until none remain. Print the result, or "
        "an empty line if the string vanishes.",
        [Param("s", STR, "lowercase letters")], OUT_STR,
        lambda s: _remove_adjacent(s),
        [("abbaca",), ("aa",)],
        lambda rng: [(word(rng, n, "ab"),) for n in (1, 2, 4, 8, 15, 40, 110, 250)],
        ["1 <= |s| <= 2000", "s contains lowercase English letters only"],
        ["Push characters onto a stack.",
         "If the incoming character equals the stack top, pop instead of pushing.",
         "The stack contents, bottom to top, are the answer.",
         "This handles cascading deletions automatically in one pass."],
        explanations=["abbaca -> aaca -> ca.", "The whole string cancels."],
    ))

    add(P(
        "decode-nested-repeat-string", "Decode Repeated String", "medium", T + ["Strings"], SQ,
        "The string `s` uses the form `k[content]` meaning the content repeats `k` times, and may nest. "
        "Print the decoded string.",
        [Param("s", STR, "digits, lowercase letters and brackets")], OUT_STR,
        lambda s: _decode_string(s),
        [("3[a]2[bc]",), ("2[a3[b]]",)],
        lambda rng: [(_encoded_case(rng, depth),) for depth in (1, 1, 2, 2, 3, 3, 4)],
        ["1 <= |s| <= 200", "repeat counts are single digits 1-9",
         "the decoded string is at most 10^5 characters"],
        ["Use two stacks: one for pending counts, one for pending prefixes.",
         "On '[' push the current count and prefix, then reset them.",
         "On ']' pop and append the repeated segment to the popped prefix.",
         "Recursive descent parsing is an equally valid approach."],
        explanations=["aaabcbc.", "abbbabbb."],
    ))

    add(P(
        "sort-stack-values", "Sort Using Stack Operations", "easy", T + ["Sorting & Searching"], SQ,
        "The array `nums` lists stack contents from bottom to top. Print the contents after sorting so "
        "the largest value ends on top, again from bottom to top.",
        [p_nums()], OUT_INT_LIST, sorted,
        [([3, 1, 2],), ([5],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["The classic exercise sorts a stack using only one auxiliary stack.",
         "Pop from the source and insert into the helper in order, pushing back while the top is larger.",
         "Reading bottom to top, the result is simply the sorted order."],
    ))

    add(P(
        "celebrity-in-party", "Find The Celebrity", "medium", T + ["Matrix"], SQ,
        "In the `n x n` matrix `mat`, `mat[i][j] = 1` means person `i` knows person `j`. A celebrity is "
        "known by everyone else and knows nobody. Print the celebrity's index, or `-1` if none exists.",
        [Param("mat", "int[][]", "the knows matrix")], OUT_INT,
        lambda mat: _find_celebrity(mat),
        [([[0, 1, 0], [0, 0, 0], [0, 1, 0]],), ([[0, 1], [1, 0]],)],
        lambda rng: [(_celebrity_matrix(rng, n),) for n in (1, 2, 3, 4, 6, 9, 14)],
        ["1 <= n <= 200", "mat[i][j] is 0 or 1", "mat[i][i] is 0"],
        ["Push all candidates on a stack, then repeatedly compare the top two.",
         "If a knows b, a cannot be the celebrity; otherwise b cannot be.",
         "One candidate survives after n-1 comparisons; verify it against every row and column.",
         "Verification is essential — the elimination only produces a candidate."],
        explanations=["Person 1 is known by 0 and 2 and knows nobody.", "They know each other."],
        brute=lambda mat: _celebrity_brute(mat),
    ))

    add(P(
        "asteroid-collision-result", "Asteroid Collision", "medium", T + ["Arrays"], SQ,
        "Each value in `nums` is an asteroid: the magnitude is its size and the sign is its direction "
        "(positive moves right, negative moves left). When two collide the smaller explodes; equal sizes "
        "destroy both. Print the surviving asteroids in order, or an empty line if none survive.",
        [Param("nums", INT_LIST, "non-zero asteroid values")], OUT_INT_LIST,
        lambda nums: _asteroids(nums),
        [([5, 10, -5],), ([8, -8],)],
        lambda rng: [([rng.choice([1, -1]) * rng.randint(1, 12) for _ in range(n)],)
                     for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= n <= 2000", "nums[i] != 0", "-10^6 <= nums[i] <= 10^6"],
        ["Only a right-moving asteroid followed by a left-moving one can collide.",
         "Keep survivors on a stack and resolve collisions when a negative value arrives.",
         "Pop while the stack top is positive and smaller; both vanish when the sizes match.",
         "Each asteroid is pushed and popped at most once."],
        explanations=["10 destroys -5.", "Equal sizes destroy both."],
    ))

    add(P(
        "daily-temperature-wait", "Days Until Warmer", "medium", T + ["Arrays"], SQ,
        "For each position of `nums`, print how many positions you must move right to find a strictly "
        "greater value, or `0` if there is none.",
        [p_nums()], OUT_INT_LIST, lambda nums: _days_until_warmer(nums),
        [([73, 74, 75, 71, 69, 72, 76, 73],), ([5, 4],)], g_nums(0, 50),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Keep a decreasing stack of indices awaiting an answer.",
         "When a larger value arrives, pop indices and record the index difference.",
         "Anything still on the stack at the end answers 0."],
        explanations=["1,1,4,2,1,1,0,0.", "No warmer day follows."],
        brute=lambda nums: [next((j - i for j in range(i + 1, len(nums)) if nums[j] > nums[i]), 0)
                            for i in range(len(nums))],
    ))

    add(P(
        "sum-of-subarray-minimums", "Sum Of Subarray Minimums", "hard", T + ["Arrays"], SQ,
        "Print the sum of the minimum value of every contiguous subarray of `nums`.",
        [Param("nums", INT_LIST, "positive integers")], OUT_INT,
        lambda nums: _sum_subarray_minimums(nums),
        [([3, 1, 2, 4],), ([2],)],
        lambda rng: [(ints(rng, n, 1, 30),) for n in (1, 2, 3, 6, 12, 35, 110, 250)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^4",
         "the answer fits in a 64-bit signed integer"],
        ["Count how many subarrays have each element as their minimum.",
         "Use previous-smaller and next-smaller boundaries to get the left and right spans.",
         "The element contributes value * leftSpan * rightSpan.",
         "Break ties consistently (strict on one side, non-strict on the other) so no subarray is "
         "counted twice."],
        explanations=["Minimums sum to 17.", "The only subarray has minimum 2."],
        brute=lambda nums: sum(min(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _next_greater(nums):
    result = [-1] * len(nums)
    stack: list[int] = []
    for index in range(len(nums) - 1, -1, -1):
        while stack and stack[-1] <= nums[index]:
            stack.pop()
        if stack:
            result[index] = stack[-1]
        stack.append(nums[index])
    return result


def _next_smaller(nums):
    result = [-1] * len(nums)
    stack: list[int] = []
    for index in range(len(nums) - 1, -1, -1):
        while stack and stack[-1] >= nums[index]:
            stack.pop()
        if stack:
            result[index] = stack[-1]
        stack.append(nums[index])
    return result


def _previous_greater(nums):
    result = [-1] * len(nums)
    stack: list[int] = []
    for index, value in enumerate(nums):
        while stack and stack[-1] <= value:
            stack.pop()
        if stack:
            result[index] = stack[-1]
        stack.append(value)
    return result


def _previous_smaller(nums):
    result = [-1] * len(nums)
    stack: list[int] = []
    for index, value in enumerate(nums):
        while stack and stack[-1] >= value:
            stack.pop()
        if stack:
            result[index] = stack[-1]
        stack.append(value)
    return result


def _next_greater_circular(nums):
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []
    for step in range(2 * n - 1, -1, -1):
        index = step % n
        while stack and stack[-1] <= nums[index]:
            stack.pop()
        if step < n and stack:
            result[index] = stack[-1]
        stack.append(nums[index])
    return result


def _stock_span(nums):
    result = []
    stack: list[int] = []
    for index, value in enumerate(nums):
        while stack and nums[stack[-1]] <= value:
            stack.pop()
        result.append(index + 1 if not stack else index - stack[-1])
        stack.append(index)
    return result


def _span_brute(nums, index):
    span = 1
    position = index - 1
    while position >= 0 and nums[position] <= nums[index]:
        span += 1
        position -= 1
    return span


def _largest_rectangle(heights):
    stack: list[int] = []
    best = 0
    extended = list(heights) + [0]
    for index, height in enumerate(extended):
        while stack and extended[stack[-1]] > height:
            top = stack.pop()
            left = stack[-1] if stack else -1
            best = max(best, extended[top] * (index - left - 1))
        stack.append(index)
    return best


def _max_rectangle(g):
    cols = len(g[0])
    heights = [0] * cols
    best = 0
    for row in g:
        for index, ch in enumerate(row):
            heights[index] = heights[index] + 1 if ch == "1" else 0
        best = max(best, _largest_rectangle(heights))
    return best


OPERATORS = {-1001: "+", -1002: "-", -1003: "*", -1004: "/"}


def _eval_postfix(tokens):
    stack: list[int] = []
    for token in tokens:
        if token in OPERATORS:
            right = stack.pop()
            left = stack.pop()
            symbol = OPERATORS[token]
            if symbol == "+":
                stack.append(left + right)
            elif symbol == "-":
                stack.append(left - right)
            elif symbol == "*":
                stack.append(left * right)
            else:
                quotient = abs(left) // abs(right)
                stack.append(quotient if (left < 0) == (right < 0) else -quotient)
        else:
            stack.append(token)
    return stack[-1]


def _postfix_case(rng, operations):
    tokens = [rng.randint(1, 50), rng.randint(1, 50)]
    for _ in range(operations):
        tokens.append(rng.choice([-1001, -1002, -1003]))
        if rng.random() < 0.6:
            tokens.append(rng.randint(1, 50))
            tokens.append(rng.choice([-1001, -1002, -1003]))
    # Ensure the expression is valid: one operator per extra operand.
    operands = sum(1 for t in tokens if t not in OPERATORS)
    operators = sum(1 for t in tokens if t in OPERATORS)
    while operators < operands - 1:
        tokens.append(-1001)
        operators += 1
    while operators > operands - 1:
        tokens.insert(0, rng.randint(1, 50))
        operands += 1
    return tokens


def _min_stack(ops):
    values: list[int] = []
    minima: list[int] = []
    answers = []
    for op in ops:
        if op >= 0:
            values.append(op)
            minima.append(op if not minima else min(minima[-1], op))
        elif op == -1:
            if values:
                values.pop()
                minima.pop()
        else:
            answers.append(minima[-1] if minima else -1)
    return answers


def _min_stack_brute(ops):
    values: list[int] = []
    answers = []
    for op in ops:
        if op >= 0:
            values.append(op)
        elif op == -1:
            if values:
                values.pop()
        else:
            answers.append(min(values) if values else -1)
    return answers


def _queue_sim(ops):
    queue: list[int] = []
    head = 0
    answers = []
    for op in ops:
        if op >= 0:
            queue.append(op)
        else:
            if head < len(queue):
                answers.append(queue[head])
                head += 1
            else:
                answers.append(-1)
    return answers


def _max_depth(s):
    depth = 0
    best = 0
    for ch in s:
        if ch == "(":
            depth += 1
            best = max(best, depth)
        else:
            depth -= 1
            if depth < 0:
                return -1
    return best if depth == 0 else -1


def _remove_adjacent(s):
    stack: list[str] = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


def _decode_string(s):
    count_stack: list[int] = []
    text_stack: list[str] = []
    current = ""
    count = 0
    for ch in s:
        if ch.isdigit():
            count = count * 10 + int(ch)
        elif ch == "[":
            count_stack.append(count if count else 1)
            text_stack.append(current)
            current = ""
            count = 0
        elif ch == "]":
            repeat = count_stack.pop()
            current = text_stack.pop() + current * repeat
        else:
            current += ch
    return current


def _encoded_case(rng, depth):
    def build(level):
        if level == 0:
            return word(rng, rng.randint(1, 3), "abc")
        inner = build(level - 1)
        return f"{rng.randint(1, 4)}[{inner}]"

    parts = [build(rng.randint(1, depth)) for _ in range(rng.randint(1, 2))]
    return "".join(parts)


def _find_celebrity(mat):
    n = len(mat)
    candidate = 0
    for other in range(1, n):
        if mat[candidate][other] == 1:
            candidate = other
    for other in range(n):
        if other == candidate:
            continue
        if mat[candidate][other] == 1 or mat[other][candidate] == 0:
            return -1
    return candidate


def _celebrity_brute(mat):
    n = len(mat)
    for candidate in range(n):
        knows_nobody = all(mat[candidate][other] == 0 for other in range(n) if other != candidate)
        known_by_all = all(mat[other][candidate] == 1 for other in range(n) if other != candidate)
        if knows_nobody and known_by_all:
            return candidate
    return -1


def _celebrity_matrix(rng, n):
    mat = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and rng.random() < 0.4:
                mat[i][j] = 1
    if rng.random() < 0.5:
        star = rng.randrange(n)
        for i in range(n):
            mat[star][i] = 0
            if i != star:
                mat[i][star] = 1
    return mat


def _asteroids(nums):
    stack: list[int] = []
    for value in nums:
        alive = True
        while alive and value < 0 and stack and stack[-1] > 0:
            if stack[-1] < -value:
                stack.pop()
                continue
            if stack[-1] == -value:
                stack.pop()
            alive = False
        if alive:
            stack.append(value)
    return stack


def _days_until_warmer(nums):
    result = [0] * len(nums)
    stack: list[int] = []
    for index, value in enumerate(nums):
        while stack and nums[stack[-1]] < value:
            top = stack.pop()
            result[top] = index - top
        stack.append(index)
    return result


def _sum_subarray_minimums(nums):
    n = len(nums)
    left = [0] * n   # count of subarrays extending left where nums[i] stays the minimum
    right = [0] * n
    stack: list[int] = []
    for index in range(n):
        while stack and nums[stack[-1]] > nums[index]:
            stack.pop()
        left[index] = index - (stack[-1] if stack else -1)
        stack.append(index)
    stack.clear()
    for index in range(n - 1, -1, -1):
        while stack and nums[stack[-1]] >= nums[index]:
            stack.pop()
        right[index] = (stack[-1] if stack else n) - index
        stack.append(index)
    return sum(nums[i] * left[i] * right[i] for i in range(n))
