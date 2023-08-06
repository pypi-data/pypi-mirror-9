from Numberjack import *


def solve():
    N = 3
    grid = Matrix(N*N, N*N, 1, N*N)

    sudoku = Model([AllDiff(row) for row in grid.row],
                   [AllDiff(col) for col in grid.col],
                   [AllDiff(grid[x:x + N, y:y + N]) for x in range(0, N*N, N) for y in range(0, N * N, N)],
                   )

    solver = sudoku.load("Mistral")

    solver.startNewSearch()
    while solver.getNextSolution() == SAT:
        print grid


if __name__ == '__main__':
    solve()
