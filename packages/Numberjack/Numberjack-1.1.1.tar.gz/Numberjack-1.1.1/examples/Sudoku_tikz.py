from Numberjack import *
import os


def get_model(N, clues):
    grid = Matrix(N*N, N*N, 1, N*N)

    sudoku = Model([AllDiff(row) for row in grid.row],
                   [AllDiff(col) for col in grid.col],
                   [AllDiff(grid[x:x + N, y:y + N]) for x in range(0, N*N, N) for y in range(0, N * N, N)],
                   [(x == int(v)) for x, v in zip(grid.flat, clues) if v != '*']
                   )
    return grid, sudoku


tikzsudokupreamble = r"""
\tikzset {
  highlight/.style = {yellow, opacity=0.3},
  digit/.style = { minimum height = 5mm, minimum width=5mm, anchor=center },
  circle/.style = {draw=green!80!black, dotted, very thick},
  cross/.style = {red, opacity=.5, shorten >=1mm, shorten <=1mm, very thick, line cap=round},
  hint/.style={blue, font=\sf, minimum width=3mm, minimum height=3mm}
}

% Original code-----------------------------------------------------------
% Modified the \node to give a unique name to each one, which is the
% row number, a dash and the column number. E.g: 1-1, 4-5, etc.
\newcounter{row}
\newcounter{col}

\newcommand\setrow[9]{
    \setcounter{col}{1}
    \foreach \n in {#1, #2, #3, #4, #5, #6, #7, #8, #9} {
        \edef\x{\value{col} - 0.5}
        \edef\y{9.5 - \value{row}}
        \node[digit,name={\arabic{row}-\arabic{col}}] at (\x, \y) {\n};
        \stepcounter{col}
    }
    \stepcounter{row}
}

\def\hintcell#1#2#3{
\node at (#1-#2) {\hintbox{#3}};
}

\def\circlecell#1#2{
\draw[circle] (#1-#2) circle(4mm);
}

% UGLY code. Do not read :-)
\def\hintbox#1{
\resizebox{4.5mm}{4.5mm}{%
\tikz[scale=0.3]{%
  \def\auxc{0}
  \foreach \m in {1,...,9} {
    \pgfmathparse{mod(\auxc,3)}
    \xdef\x{\pgfmathresult}
    \pgfmathparse{-floor(\auxc/3)}
    \xdef\y{\pgfmathresult}
    \xdef\hintprinted{0}
    \foreach \n in {#1} {
      \ifnum\n=\m
       \node[hint] at (\x,\y) {\n};
       \xdef\hintprinted{1}
      \fi
     }
   \ifnum\hintprinted=0
      \node[hint, opacity=0.1] at (\x,\y) {\m};
   \fi
   \pgfmathparse{\auxc+1}
   \xdef\auxc{\pgfmathresult}   }
  }%
 }
}
"""


tikzcounter = 0


def printtikz(prefix, N, clues, grid, solver=None, highlight=None, hidehints=False):
    global tikzcounter
    tikzcounter += 1
    rowlen = N * N
    line = []
    hintlines = []
    filename = "%s%d.tex" % (prefix, tikzcounter)

    with open(filename, "wt") as f:
        print >> f, tikzsudokupreamble
        print >> f, """
\\begin{tikzpicture}[scale=.5]
\\begin{scope}
\draw (0, 0) grid (9, 9);
\draw[very thick, scale=3] (0, 0) grid (3, 3);
\setcounter{row}{1}
"""
        for index, (x, v) in enumerate(zip(grid.flat, clues)):
            i = int(index / rowlen)
            j = int(index % rowlen)
            if j == 0:
                line = ["\setrow"]
            if index % N == 0:
                line.append(" ")

            if v == "*":
                if solver is None:
                    domain = range(x.get_min(), x.get_max() + 1)
                else:
                    domain = [x.get_min(solver)]
                    while True:
                        v = solver.next(x, domain[-1])
                        if v <= domain[-1]:
                            break
                        domain.append(v)

                if len(domain) == 1:
                    line.append("{%d}" % domain[0])
                else:
                    line.append("{ }")
                    hintstr = ",".join(map(str, domain))
                    hintlines.append("\hintcell{%d}{%d}{%s}" % (i + 1, j + 1, hintstr))
            else:
                line.append("{%s}" % v)

            if j == rowlen - 1:
                if i % N == 0:
                    print >> f
                print >> f, "".join(line)

        if not hidehints:
            for line in hintlines:
                print >> f, line

        if highlight:
            print >> f, "\circlecell{%d}{%d}" % tuple(highlight)

        print >> f, """
\end{scope}
\end{tikzpicture}
"""


def solve(param):
    N = param['N']
    cluesfilename = param['file']
    clues = "".join(open(cluesfilename, "rt")).split()
    grid, sudoku = get_model(N, clues)

    folder = "sudoku_tikz"
    if not os.path.isdir(folder):
        os.makedirs(folder)
    prefix = os.path.join(folder, "sudoku_")
    printtikz(prefix, N, clues, grid, hidehints=True)
    printtikz(prefix, N, clues, grid)

    solver = sudoku.load(param['solver'])
    solver.setVerbosity(param['verbose'])
    solver.setTimeLimit(param['tcutoff'])

    solver.startNewSearch()
    solver.propagate()
    printtikz(prefix, N, clues, grid, solver)

    solver = sudoku.load(param['solver'])
    solver.solve()
    printtikz(prefix, N, clues, grid, solver)
    out = ""
    # if solver.is_sat():
    out = str(grid)

    return out


def solveAllSolutions(param):
    N = param['N']
    cluesfilename = param['file']
    clues = "".join(open(cluesfilename, "rt")).split()
    grid, sudoku = get_model(N, clues)

    solver = sudoku.load(param['solver'])
    solver.setVerbosity(param['verbose'])
    solver.setTimeLimit(param['tcutoff'])

    solver.startNewSearch()
    while solver.getNextSolution():
        print str(grid)


def solve_custom(param):
    N = param['N']
    cluesfilename = param['file']
    clues = "".join(open(cluesfilename, "rt")).split()
    grid, sudoku = get_model(N, clues)

    folder = "sudoku_tikz"
    if not os.path.isdir(folder):
        os.makedirs(folder)
    prefix = os.path.join(folder, "sudokucustom_")
    printtikz(prefix, N, clues, grid)

    solver = sudoku.load(param['solver'])
    solver.setVerbosity(param['verbose'])
    solver.setTimeLimit(param['tcutoff'])
    solver.startNewSearch()

    proven_infeasibility = False
    prevvar, prevval = None, None
    depth = 0

    def log(s):
        print "  " * depth, s

    def variableselection(variables):
        minsel = [None, None, sys.maxint]
        for i, v in enumerate(variables):
            size = v.get_size()
            if size > 1 and size < minsel[2]:
                minsel = [v, i, size]
        return minsel[0], minsel[1]

    variables = grid.flat
    while not proven_infeasibility:
        if solver.propagate():  # Propagate to a fixed point. Returns False if there was a conflict
            # left branch
            # log("Variable domains at depth %d:" % depth)
            # for x in variables:
            #     log(x)

            x, ind = variableselection(variables)
            if x is None:  # Complete, no more variables to assign
                return solver.get_solution()
            v = x.get_min()
            row, col = int(ind / (N * N)) + 1, int(ind % (N * N)) + 1
            print x.name(), ind, row, col
            printtikz(prefix, N, clues, grid, solver, highlight=(row, col))

            prevvar, prevval = x.name(), v  # Save for debugging output
            log("Decision: %s == %d" % (prevvar, prevval))

            solver.save()
            solver.post(x == v)
            depth += 1

        else:  # right branch
            proven_infeasibility = not solver.undo()
            if not proven_infeasibility:
                solver.deduce()  # Invert the previous decision, i.e. x != v
                log("Deduce: %s != %d" % (prevvar, prevval))
                depth -= 1

    return None


default = {'N': 3, 'solver': 'Mistral', 'file': 'data/sudoku_hardest.txt', 'verbose': 0, 'tcutoff': 30}


if __name__ == '__main__':
    param = input(default)
    solveAllSolutions(param)
    # print solve(param)
    # print solve_custom(param)
