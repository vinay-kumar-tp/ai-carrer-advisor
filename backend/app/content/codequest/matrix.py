"""2-D grid and matrix problems."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    GRID,
    MATRIX,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_MATRIX,
    P,
    Param,
    grid,
    matrix,
    p_int,
)

T = ["Matrix"]
MT = ["Matrix Traversal"]


def p_mat(name="mat", desc="the matrix"):
    return Param(name, MATRIX, desc)


def g_mat(lo=-20, hi=20, shapes=((1, 1), (1, 3), (3, 1), (2, 2), (3, 4), (5, 5), (8, 6), (12, 10))):
    def gen(rng: random.Random):
        return [(matrix(rng, r, c, lo, hi),) for r, c in shapes]

    return gen


def g_square(lo=-20, hi=20, sizes=(1, 2, 3, 4, 5, 7, 10, 15)):
    def gen(rng: random.Random):
        return [(matrix(rng, n, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "matrix-sum", "Matrix Sum", "easy", T, MT,
        "Print the sum of every element of the matrix `mat`.",
        [p_mat()], OUT_INT, lambda mat: sum(sum(row) for row in mat),
        [([[1, 2], [3, 4]],), ([[5]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Nest two loops over rows and columns.",
         "Accumulate into a single total.",
         "Summing each row and adding the row sums works equally well."],
        explanations=["1+2+3+4 = 10.", "A 1x1 matrix sums to its only element."],
    ))

    add(P(
        "matrix-row-sums", "Row Sums", "easy", T, MT,
        "Print the sum of each row of `mat`, space separated, top row first.",
        [p_mat()], OUT_INT_LIST, lambda mat: [sum(row) for row in mat],
        [([[1, 2], [3, 4]],), ([[7, 7, 7]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Sum each row independently.", "Output one value per row.",
         "The number of results equals the row count."],
    ))

    add(P(
        "matrix-column-sums", "Column Sums", "easy", T, MT,
        "Print the sum of each column of `mat`, space separated, leftmost column first.",
        [p_mat()], OUT_INT_LIST,
        lambda mat: [sum(row[c] for row in mat) for c in range(len(mat[0]))],
        [([[1, 2], [3, 4]],), ([[1], [2]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Loop columns on the outside and rows on the inside.",
         "Or keep a running total per column in a single pass over the matrix.",
         "The number of results equals the column count."],
    ))

    add(P(
        "matrix-transpose", "Transpose Matrix", "easy", T, MT,
        "Print the transpose of `mat`: the element at row `i`, column `j` moves to row `j`, column `i`.",
        [p_mat()], OUT_MATRIX,
        lambda mat: [[mat[r][c] for r in range(len(mat))] for c in range(len(mat[0]))],
        [([[1, 2, 3], [4, 5, 6]],), ([[9]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["The result has c rows and r columns.",
         "Read down the columns of the input to build each output row.",
         "A square matrix can be transposed in place by swapping across the diagonal."],
    ))

    add(P(
        "rotate-matrix-90-clockwise", "Rotate Matrix 90 Degrees", "medium", T, MT,
        "Rotate the square matrix `mat` by 90 degrees clockwise and print the result.",
        [p_mat("mat", "a square matrix")], OUT_MATRIX,
        lambda mat: [list(row) for row in zip(*mat[::-1])],
        [([[1, 2], [3, 4]],), ([[5]],)], g_square(),
        ["1 <= n <= 200", "mat is square", "-10^6 <= mat[i][j] <= 10^6"],
        ["Transpose the matrix, then reverse each row.",
         "Equivalently reverse the row order first, then transpose.",
         "In place you can rotate four cells at a time, ring by ring."],
        explanations=["[[1,2],[3,4]] becomes [[3,1],[4,2]].", "A 1x1 matrix is unchanged."],
    ))

    add(P(
        "rotate-matrix-180", "Rotate Matrix 180 Degrees", "easy", T, MT,
        "Rotate the matrix `mat` by 180 degrees and print the result.",
        [p_mat()], OUT_MATRIX,
        lambda mat: [list(reversed(row)) for row in reversed(mat)],
        [([[1, 2], [3, 4]],), ([[1, 2, 3]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Reverse the order of the rows and also reverse each row.",
         "That is the same as applying the 90-degree rotation twice.",
         "The shape stays r x c."],
    ))

    add(P(
        "rotate-matrix-90-counter", "Rotate Matrix Counter Clockwise", "medium", T, MT,
        "Rotate the square matrix `mat` by 90 degrees counter-clockwise and print the result.",
        [p_mat("mat", "a square matrix")], OUT_MATRIX,
        lambda mat: [list(row) for row in zip(*mat)][::-1],
        [([[1, 2], [3, 4]],), ([[7]],)], g_square(),
        ["1 <= n <= 200", "mat is square", "-10^6 <= mat[i][j] <= 10^6"],
        ["Transpose, then reverse the row order.",
         "That is the mirror of the clockwise recipe.",
         "Applying it four times returns the original."],
        explanations=["[[1,2],[3,4]] becomes [[2,4],[1,3]].", "A 1x1 matrix is unchanged."],
    ))

    add(P(
        "spiral-order-traversal", "Spiral Order", "medium", T, MT,
        "Print the elements of `mat` in spiral order: left to right along the top row, down the right "
        "column, right to left along the bottom, up the left column, then inwards.",
        [p_mat()], OUT_INT_LIST, lambda mat: _spiral(mat),
        [([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[1, 2]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Track four boundaries: top, bottom, left and right.",
         "Walk one edge at a time, then shrink that boundary.",
         "Check that top <= bottom and left <= right before the bottom row and left column passes, "
         "otherwise single-row or single-column leftovers get visited twice.",
         "Every cell is printed exactly once."],
        explanations=["1,2,3,6,9,8,7,4,5.", "A single row is already in order."],
        brute=lambda mat: _spiral_brute(mat),
    ))

    add(P(
        "diagonal-sums", "Diagonal Sums", "easy", T, MT,
        "For the square matrix `mat`, print the sum of the primary diagonal followed by the sum of the "
        "secondary diagonal.",
        [p_mat("mat", "a square matrix")], OUT_INT_LIST,
        lambda mat: [sum(mat[i][i] for i in range(len(mat))),
                     sum(mat[i][len(mat) - 1 - i] for i in range(len(mat)))],
        [([[1, 2], [3, 4]],), ([[5]],)], g_square(),
        ["1 <= n <= 200", "mat is square", "-10^6 <= mat[i][j] <= 10^6"],
        ["The primary diagonal is where row equals column.",
         "The secondary diagonal is where row + column equals n - 1.",
         "For odd n the centre cell belongs to both diagonals."],
        out_desc="Print `primarySum secondarySum`.",
        explanations=["1+4 = 5 and 2+3 = 5.", "The single element belongs to both diagonals."],
    ))

    add(P(
        "matrix-boundary-sum", "Boundary Sum", "easy", T, MT,
        "Print the sum of the elements on the border of `mat` (first and last row, first and last "
        "column), counting each cell once.",
        [p_mat()], OUT_INT, lambda mat: _boundary_sum(mat),
        [([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[4]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["A cell is on the border when its row or column is the first or last.",
         "Iterate every cell and test that condition to avoid double counting corners.",
         "For a 1x1 matrix the single cell is the whole border."],
        explanations=["Everything except the centre 5 sums to 40.", "The only cell is on the border."],
    ))

    add(P(
        "is-identity-matrix", "Identity Matrix Check", "easy", T, MT,
        "Print `YES` if the square matrix `mat` is the identity matrix (ones on the primary diagonal, "
        "zeros elsewhere), else `NO`.",
        [p_mat("mat", "a square matrix")], OUT_BOOL,
        lambda mat: all(mat[i][j] == (1 if i == j else 0) for i in range(len(mat)) for j in range(len(mat))),
        [([[1, 0], [0, 1]],), ([[1, 1], [0, 1]],)],
        lambda rng: [(_maybe_identity(rng, n),) for n in (1, 2, 3, 4, 6, 9, 12)],
        ["1 <= n <= 200", "mat is square"],
        ["Check the diagonal holds 1 and everything else holds 0.",
         "Stop at the first violation.",
         "A 1x1 matrix is the identity exactly when its element is 1."],
    ))

    add(P(
        "is-symmetric-matrix", "Symmetric Matrix Check", "easy", T, MT,
        "Print `YES` if the square matrix `mat` equals its own transpose, else `NO`.",
        [p_mat("mat", "a square matrix")], OUT_BOOL,
        lambda mat: all(mat[i][j] == mat[j][i] for i in range(len(mat)) for j in range(len(mat))),
        [([[1, 2], [2, 1]],), ([[1, 2], [3, 1]],)],
        lambda rng: [(_maybe_symmetric(rng, n),) for n in (1, 2, 3, 4, 6, 9, 12)],
        ["1 <= n <= 200", "mat is square", "-10^6 <= mat[i][j] <= 10^6"],
        ["Compare mat[i][j] with mat[j][i].",
         "Only the upper triangle needs checking, halving the work.",
         "The diagonal is always equal to itself."],
    ))

    add(P(
        "matrix-multiplication", "Matrix Multiplication", "medium", T, MT,
        "Multiply the `r x k` matrix `a` by the `k x c` matrix `b` and print the resulting `r x c` matrix.",
        [Param("a", MATRIX, "left matrix"), Param("b", MATRIX, "right matrix")], OUT_MATRIX,
        lambda a, b: _multiply(a, b),
        [([[1, 2], [3, 4]], [[5, 6], [7, 8]]), ([[2]], [[3]])],
        lambda rng: [(matrix(rng, r, k, -9, 9), matrix(rng, k, c, -9, 9))
                     for r, k, c in ((1, 1, 1), (2, 3, 2), (3, 2, 4), (4, 4, 4), (6, 5, 3), (10, 8, 7))],
        ["1 <= r, k, c <= 60", "-100 <= values <= 100",
         "the column count of a always equals the row count of b"],
        ["Each output cell is a dot product of a row of a with a column of b.",
         "Three nested loops give O(r*k*c).",
         "Initialise every accumulator to 0 before adding."],
        explanations=["[[19,22],[43,50]].", "A 1x1 product is just 6."],
    ))

    add(P(
        "matrix-addition", "Matrix Addition", "easy", T, MT,
        "Add the two matrices `a` and `b` of identical shape element by element and print the result.",
        [Param("a", MATRIX, "first matrix"), Param("b", MATRIX, "second matrix")], OUT_MATRIX,
        lambda a, b: [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))],
        [([[1, 2], [3, 4]], [[5, 6], [7, 8]]), ([[1]], [[-1]])],
        lambda rng: [(matrix(rng, r, c, -50, 50), matrix(rng, r, c, -50, 50))
                     for r, c in ((1, 1), (2, 3), (3, 2), (4, 4), (7, 5), (10, 9))],
        ["1 <= r, c <= 200", "both matrices share the same shape", "-10^6 <= values <= 10^6"],
        ["Walk both matrices with the same indices.",
         "Add matching cells.",
         "The result keeps the same shape."],
    ))

    add(P(
        "search-in-sorted-matrix", "Search Row-Column Sorted Matrix", "medium",
        T + ["Binary Search"], ["Modified Binary Search"],
        "Every row of `mat` is sorted left to right and every column is sorted top to bottom. Print "
        "`YES` if `target` appears, else `NO`.",
        [p_mat("mat", "rows and columns are sorted ascending"), p_int("target", "value to find")],
        OUT_BOOL, lambda mat, target: _staircase_search(mat, target),
        [([[1, 4, 7], [2, 5, 8], [3, 6, 9]], 5), ([[1, 2]], 3)],
        lambda rng: [(_sorted_matrix(rng, r, c), rng.randint(0, 40))
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (5, 4), (8, 6), (12, 10))],
        ["1 <= r, c <= 200", "rows and columns are sorted in non-decreasing order",
         "-10^6 <= values, target <= 10^6"],
        ["Start at the top-right corner.",
         "If the current value is larger than the target move left, otherwise move down.",
         "Each step eliminates a whole row or column, giving O(r + c).",
         "Binary searching each row is also acceptable at O(r log c)."],
        explanations=["5 sits in the middle.", "3 is absent."],
        brute=lambda mat, target: any(target in row for row in mat),
    ))

    add(P(
        "set-matrix-zeroes", "Set Matrix Zeroes", "medium", T, MT,
        "If any cell of `mat` is `0`, set that cell's whole row and column to `0`. Print the resulting "
        "matrix.",
        [p_mat()], OUT_MATRIX, lambda mat: _set_zeroes(mat),
        [([[1, 1, 1], [1, 0, 1], [1, 1, 1]],), ([[0, 2]],)],
        lambda rng: [([[rng.choice([0, 0, rng.randint(1, 9)]) for _ in range(c)] for _ in range(r)],)
                     for r, c in ((1, 1), (1, 3), (3, 1), (2, 2), (3, 4), (5, 5), (8, 7))],
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Record which rows and columns must be cleared before changing anything.",
         "Clearing as you scan would cascade and wipe the whole matrix.",
         "Two boolean arrays of size r and c are enough — O(r + c) extra space.",
         "The first row and column can store those flags for O(1) extra space."],
        explanations=["The middle 0 clears row 1 and column 1.", "The 0 clears the only row and its column."],
        brute=lambda mat: _set_zeroes_brute(mat),
    ))

    add(P(
        "count-negative-numbers-matrix", "Count Negatives In Matrix", "easy", T, MT,
        "Print how many elements of `mat` are negative.",
        [p_mat()], OUT_INT, lambda mat: sum(1 for row in mat for value in row if value < 0),
        [([[1, -1], [-2, 3]],), ([[5]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["A single scan with a counter is O(r*c).",
         "If rows are sorted you can binary search the first negative per row.",
         "Print 0 when nothing is negative."],
    ))

    add(P(
        "max-row-sum-index", "Row With Maximum Sum", "easy", T, MT,
        "Print the 0-based index of the row of `mat` with the largest sum. If several tie, print the "
        "smallest index.",
        [p_mat()], OUT_INT,
        lambda mat: max(range(len(mat)), key=lambda i: (sum(mat[i]), -i)),
        [([[1, 2], [5, 0]],), ([[1], [1]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Compute each row sum and track the best.",
         "Replace the best only on a strictly larger sum so ties keep the earlier row.",
         "One pass over the matrix suffices."],
        explanations=["Row 1 sums to 5, beating row 0's 3.", "Both rows sum to 1, so index 0 wins."],
    ))

    add(P(
        "transpose-in-place-square", "Diagonal Mirror", "easy", T, MT,
        "Mirror the square matrix `mat` across its primary diagonal and print the result (this is the "
        "in-place transpose).",
        [p_mat("mat", "a square matrix")], OUT_MATRIX,
        lambda mat: [[mat[j][i] for j in range(len(mat))] for i in range(len(mat))],
        [([[1, 2], [3, 4]],), ([[8]],)], g_square(),
        ["1 <= n <= 200", "mat is square", "-10^6 <= mat[i][j] <= 10^6"],
        ["Swap mat[i][j] with mat[j][i] for every j > i.",
         "Iterating the full matrix would swap each pair twice, undoing the work.",
         "The diagonal itself never moves."],
    ))

    add(P(
        "island-count-grid", "Count Islands", "medium", T + ["Graphs"], ["BFS / Connected Components"],
        "The grid `g` uses `1` for land and `0` for water. Two land cells belong to the same island "
        "when they touch horizontally or vertically. Print the number of islands.",
        [Param("g", GRID, "rows of 0/1 characters")], OUT_INT,
        lambda g: _count_islands(g),
        [(["110", "010", "001"],), (["0"],)],
        lambda rng: [(grid(rng, r, c, "01"),) for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (5, 5), (8, 6), (12, 10))],
        ["1 <= r, c <= 200", "each character is 0 or 1"],
        ["Scan for an unvisited land cell, then flood fill from it.",
         "Each flood fill you start corresponds to exactly one island.",
         "BFS with a queue or DFS with a stack both work; recursion can overflow on large grids.",
         "Only the four orthogonal neighbours count, not diagonals."],
        explanations=["Cells (0,0),(0,1),(1,1) form one island and (2,2) forms another.",
                      "There is no land."],
    ))

    add(P(
        "max-area-island", "Largest Island Area", "medium", T + ["Graphs"], ["BFS / Connected Components"],
        "In the `0`/`1` grid `g`, print the number of cells in the largest orthogonally connected group "
        "of `1`s. Print `0` if there is no land.",
        [Param("g", GRID, "rows of 0/1 characters")], OUT_INT,
        lambda g: _max_island(g),
        [(["110", "010", "001"],), (["00"],)],
        lambda rng: [(grid(rng, r, c, "01"),) for r, c in ((1, 1), (1, 5), (5, 1), (3, 3), (5, 5), (9, 7), (14, 11))],
        ["1 <= r, c <= 200", "each character is 0 or 1"],
        ["Flood fill each island and count the cells you visit.",
         "Track the maximum count across all fills.",
         "Mark cells visited as you go so no cell is counted twice."],
        explanations=["The larger island has 3 cells.", "No land at all."],
    ))

    add(P(
        "flood-fill-count-changed", "Flood Fill Region Size", "medium", T + ["Graphs"],
        ["BFS / Connected Components"],
        "Starting from cell `(sr, sc)` of the `0`/`1` grid `g`, print how many cells belong to the "
        "orthogonally connected region sharing that starting cell's value.",
        [Param("g", GRID, "rows of 0/1 characters"), p_int("sr", "start row"), p_int("sc", "start column")],
        OUT_INT, lambda g, sr, sc: _region_size(g, sr, sc),
        [(["110", "010", "001"], 0, 0), (["0"], 0, 0)],
        lambda rng: [(lambda gg: (gg, rng.randrange(len(gg)), rng.randrange(len(gg[0]))))(grid(rng, r, c, "01"))
                     for r, c in ((1, 1), (2, 3), (3, 3), (5, 4), (8, 6), (11, 9))],
        ["1 <= r, c <= 200", "0 <= sr < r", "0 <= sc < c", "each character is 0 or 1"],
        ["Flood fill from the start, only stepping onto cells with the same value.",
         "Count every cell you mark as visited.",
         "The starting cell always counts, so the answer is at least 1."],
        explanations=["The region of 1s containing (0,0) has 3 cells.", "The single cell forms its own region."],
    ))

    add(P(
        "matrix-zigzag-traversal", "Zigzag Row Traversal", "easy", T, MT,
        "Print the elements of `mat` reading the first row left to right, the second row right to left, "
        "and so on, alternating direction.",
        [p_mat()], OUT_INT_LIST,
        lambda mat: [value for i, row in enumerate(mat) for value in (row if i % 2 == 0 else row[::-1])],
        [([[1, 2, 3], [4, 5, 6]],), ([[7]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Use the row index's parity to pick the direction.",
         "Even rows read forwards, odd rows read backwards.",
         "Every element appears exactly once."],
        explanations=["Row 0 forwards then row 1 backwards: 1,2,3,6,5,4.", "One element."],
    ))

    add(P(
        "matrix-diagonal-traversal", "Diagonal Traversal", "medium", T, MT,
        "Print the elements of `mat` grouped by the value of `row + column`, ascending. Within each "
        "group list cells by increasing row index.",
        [p_mat()], OUT_INT_LIST, lambda mat: _diagonal_order(mat),
        [([[1, 2], [3, 4]],), ([[1, 2, 3]],)], g_mat(),
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Cells on the same anti-diagonal share the sum row + column.",
         "That sum ranges from 0 to r + c - 2.",
         "For each sum, iterate valid rows in increasing order."],
        explanations=["Sums 0,1,1,2 give 1,2,3,4.", "Sums 0,1,2 give 1,2,3."],
    ))

    add(P(
        "count-paths-grid-obstacles", "Unique Paths With Obstacles", "medium",
        T + ["Dynamic Programming"], ["Grid / 2-D DP"],
        "You start at the top-left of the `0`/`1` grid `g` and must reach the bottom-right, moving only "
        "right or down. Cells marked `1` are blocked. Print the number of distinct paths.",
        [Param("g", GRID, "rows of 0/1, where 1 is blocked")], OUT_INT,
        lambda g: _unique_paths(g),
        [(["000", "010", "000"],), (["1"],)],
        lambda rng: [(_sparse_grid(rng, r, c),) for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (4, 5), (7, 6), (10, 9))],
        ["1 <= r, c <= 100", "each character is 0 or 1",
         "the answer fits in a 64-bit signed integer"],
        ["dp[i][j] counts paths reaching that cell.",
         "A free cell inherits dp[i-1][j] + dp[i][j-1]; a blocked cell contributes 0.",
         "Start with dp[0][0] = 1 unless the start itself is blocked.",
         "A blocked start or finish makes the answer 0."],
        explanations=["Two paths dodge the central obstacle.", "The start is blocked."],
    ))

    add(P(
        "min-path-sum-grid", "Minimum Path Sum", "medium", T + ["Dynamic Programming"], ["Grid / 2-D DP"],
        "Starting at the top-left of `mat` and moving only right or down, print the smallest possible "
        "sum of the visited cells when you reach the bottom-right.",
        [p_mat("mat", "non-negative values")], OUT_INT, lambda mat: _min_path_sum(mat),
        [([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), ([[5]],)],
        lambda rng: [(matrix(rng, r, c, 0, 20),) for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (4, 5), (7, 6), (12, 10))],
        ["1 <= r, c <= 200", "0 <= mat[i][j] <= 10^4"],
        ["dp[i][j] is the cheapest cost to reach that cell.",
         "It equals mat[i][j] plus the cheaper of the cell above and the cell to the left.",
         "The first row and column have only one predecessor each.",
         "A single row of DP values is enough for O(c) space."],
        explanations=["1->3->1->1->1 costs 7.", "The only cell costs 5."],
    ))

    add(P(
        "max-path-sum-grid", "Maximum Path Sum Grid", "medium", T + ["Dynamic Programming"],
        ["Grid / 2-D DP"],
        "Starting at the top-left of `mat` and moving only right or down, print the largest possible sum "
        "of the visited cells when you reach the bottom-right.",
        [p_mat()], OUT_INT, lambda mat: _max_path_sum(mat),
        [([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), ([[-5]],)],
        lambda rng: [(matrix(rng, r, c, -20, 20),) for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (4, 5), (7, 6), (12, 10))],
        ["1 <= r, c <= 200", "-10^4 <= mat[i][j] <= 10^4"],
        ["Mirror the minimum-path DP but take the maximum instead.",
         "Negative values are fine — you must still reach the corner.",
         "The first row and column accumulate in one direction only."],
        explanations=["1->3->5->2->1 gives 12.", "Only one cell to take."],
    ))

    add(P(
        "count-cells-with-value", "Count Value In Matrix", "easy", T, MT,
        "Print how many cells of `mat` equal `target`.",
        [p_mat(), p_int("target")], OUT_INT,
        lambda mat, target: sum(1 for row in mat for value in row if value == target),
        [([[1, 2], [2, 3]], 2), ([[1]], 5)],
        lambda rng: [(matrix(rng, r, c, 1, 5), rng.randint(1, 6))
                     for r, c in ((1, 1), (2, 2), (3, 4), (5, 5), (8, 7), (12, 10))],
        ["1 <= r, c <= 200", "-10^6 <= values, target <= 10^6"],
        ["Scan all cells and count the matches.",
         "Print 0 when the value never appears.",
         "This is O(r*c) which is unavoidable for an unsorted matrix."],
    ))

    add(P(
        "saddle-point-value", "Saddle Point", "medium", T, MT,
        "A saddle point is a cell that is the minimum of its row and the maximum of its column. Print "
        "the value of any saddle point, or `-1` if none exists. If several exist, print the one in the "
        "smallest row index (then smallest column).",
        [p_mat()], OUT_INT, lambda mat: _saddle_point(mat),
        [([[3, 4, 5], [1, 2, 6], [7, 8, 9]],), ([[1, 2], [3, 4]],)],
        lambda rng: [(matrix(rng, r, c, 1, 6),) for r, c in ((1, 1), (2, 2), (3, 3), (4, 4), (5, 6), (8, 7))],
        ["1 <= r, c <= 200", "-10^6 <= mat[i][j] <= 10^6"],
        ["Precompute each row's minimum and each column's maximum.",
         "Then a cell qualifies when it equals both.",
         "Scanning rows in order, then columns in order, yields the required tie-break.",
         "In a 1x1 matrix the only cell is always a saddle point."],
        explanations=["7 is the minimum of its row and the maximum of its column.",
                      "No cell satisfies both conditions."],
        brute=lambda mat: _saddle_brute(mat),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _spiral(mat):
    top, bottom = 0, len(mat) - 1
    left, right = 0, len(mat[0]) - 1
    result = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(mat[top][c])
        top += 1
        for r in range(top, bottom + 1):
            result.append(mat[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(mat[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(mat[r][left])
            left += 1
    return result


def _spiral_brute(mat):
    rows, cols = len(mat), len(mat[0])
    seen = [[False] * cols for _ in range(rows)]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    r = c = d = 0
    result = []
    for _ in range(rows * cols):
        result.append(mat[r][c])
        seen[r][c] = True
        nr, nc = r + directions[d][0], c + directions[d][1]
        if not (0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc]):
            d = (d + 1) % 4
            nr, nc = r + directions[d][0], c + directions[d][1]
        r, c = nr, nc
    return result


def _boundary_sum(mat):
    rows, cols = len(mat), len(mat[0])
    total = 0
    for r in range(rows):
        for c in range(cols):
            if r in (0, rows - 1) or c in (0, cols - 1):
                total += mat[r][c]
    return total


def _maybe_identity(rng, n):
    if rng.random() < 0.4:
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    return [[rng.randint(0, 1) for _ in range(n)] for _ in range(n)]


def _maybe_symmetric(rng, n):
    base = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
    if rng.random() < 0.45:
        for i in range(n):
            for j in range(i):
                base[i][j] = base[j][i]
    return base


def _multiply(a, b):
    rows, inner, cols = len(a), len(b), len(b[0])
    result = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            if a[i][k] == 0:
                continue
            for j in range(cols):
                result[i][j] += a[i][k] * b[k][j]
    return result


def _sorted_matrix(rng, r, c):
    mat = [[0] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            candidates = [0]
            if i:
                candidates.append(mat[i - 1][j])
            if j:
                candidates.append(mat[i][j - 1])
            mat[i][j] = max(candidates) + rng.randint(0, 3)
    return mat


def _staircase_search(mat, target):
    r, c = 0, len(mat[0]) - 1
    while r < len(mat) and c >= 0:
        value = mat[r][c]
        if value == target:
            return True
        if value > target:
            c -= 1
        else:
            r += 1
    return False


def _set_zeroes(mat):
    rows, cols = len(mat), len(mat[0])
    zero_rows = {r for r in range(rows) if any(mat[r][c] == 0 for c in range(cols))}
    zero_cols = {c for c in range(cols) if any(mat[r][c] == 0 for r in range(rows))}
    return [[0 if r in zero_rows or c in zero_cols else mat[r][c] for c in range(cols)] for r in range(rows)]


def _set_zeroes_brute(mat):
    rows, cols = len(mat), len(mat[0])
    result = [row[:] for row in mat]
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                for cc in range(cols):
                    result[r][cc] = 0
                for rr in range(rows):
                    result[rr][c] = 0
    return result


def _count_islands(g):
    rows, cols = len(g), len(g[0])
    seen = [[False] * cols for _ in range(rows)]
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "1" and not seen[r][c]:
                islands += 1
                stack = [(r, c)]
                seen[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == "1" and not seen[nr][nc]:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
    return islands


def _max_island(g):
    rows, cols = len(g), len(g[0])
    seen = [[False] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "1" and not seen[r][c]:
                size = 0
                stack = [(r, c)]
                seen[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    size += 1
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == "1" and not seen[nr][nc]:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
                best = max(best, size)
    return best


def _region_size(g, sr, sc):
    rows, cols = len(g), len(g[0])
    target = g[sr][sc]
    seen = [[False] * cols for _ in range(rows)]
    seen[sr][sc] = True
    stack = [(sr, sc)]
    size = 0
    while stack:
        r, c = stack.pop()
        size += 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == target and not seen[nr][nc]:
                seen[nr][nc] = True
                stack.append((nr, nc))
    return size


def _diagonal_order(mat):
    rows, cols = len(mat), len(mat[0])
    result = []
    for total in range(rows + cols - 1):
        for r in range(rows):
            c = total - r
            if 0 <= c < cols:
                result.append(mat[r][c])
    return result


def _sparse_grid(rng, r, c):
    rows = []
    for _ in range(r):
        rows.append("".join("1" if rng.random() < 0.22 else "0" for _ in range(c)))
    return rows


def _unique_paths(g):
    rows, cols = len(g), len(g[0])
    if g[0][0] == "1":
        return 0
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = 1
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "1":
                dp[r][c] = 0
                continue
            if r:
                dp[r][c] += dp[r - 1][c]
            if c:
                dp[r][c] += dp[r][c - 1]
    return dp[rows - 1][cols - 1]


def _min_path_sum(mat):
    rows, cols = len(mat), len(mat[0])
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            best = None
            if r:
                best = dp[r - 1][c]
            if c:
                best = dp[r][c - 1] if best is None else min(best, dp[r][c - 1])
            dp[r][c] = mat[r][c] + (best if best is not None else 0)
    return dp[rows - 1][cols - 1]


def _max_path_sum(mat):
    rows, cols = len(mat), len(mat[0])
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            best = None
            if r:
                best = dp[r - 1][c]
            if c:
                best = dp[r][c - 1] if best is None else max(best, dp[r][c - 1])
            dp[r][c] = mat[r][c] + (best if best is not None else 0)
    return dp[rows - 1][cols - 1]


def _saddle_point(mat):
    rows, cols = len(mat), len(mat[0])
    row_min = [min(row) for row in mat]
    col_max = [max(mat[r][c] for r in range(rows)) for c in range(cols)]
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == row_min[r] and mat[r][c] == col_max[c]:
                return mat[r][c]
    return -1


def _saddle_brute(mat):
    rows, cols = len(mat), len(mat[0])
    for r in range(rows):
        for c in range(cols):
            value = mat[r][c]
            if all(value <= mat[r][cc] for cc in range(cols)) and all(value >= mat[rr][c] for rr in range(rows)):
                return value
    return -1
