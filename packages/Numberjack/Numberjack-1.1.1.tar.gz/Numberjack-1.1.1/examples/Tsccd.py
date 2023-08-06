from Numberjack import *


def get_model(k, v, n):
    design = Matrix(v, n)
    pairs = Matrix(v * (v - 1) / 2, n)
    index = [[0 for i in range(v)] for j in range(v)]
    a = 0
    for i in range(v - 1):
        for j in range(i + 1, v):
            index[i][j] = a
            index[j][i] = a
            a += 1

    pair_occurrence = VarArray(v * (v - 1) / 2, 1, v - k)

    first = VarArray(v * (v - 1) / 2, n)
    last = VarArray(v * (v - 1) / 2, n)

    model = Model(
        ## each block is a k-tuple
        [Sum(col) == k for col in design.col],

        ## exactly one change between each block
        [Sum([design[i][j - 1] > design[i][j] for i in range(v)]) == 1 for j in range(1, n)],
        [Sum([design[i][j - 1] < design[i][j] for i in range(v)]) == 1 for j in range(1, n)],

        ## each pair can occur between 1 and v-k times
        [pairs[index[i][j]][x] == (design[i][x] & design[j][x]) for i in range(v) for j in range(i) for x in range(n)],
        [pair_occurrence[index[i][j]] == Sum(pairs[index[i][j]])],

        ## consecutive ones (convex rows)
        [pairs[index[i][j]][x] <= (first[index[i][j]] <= x) for i in range(v) for j in range(i) for x in range(n)],
        [pairs[index[i][j]][x] <= (last[index[i][j]] >= x) for i in range(v) for j in range(i) for x in range(n)],
        [((first[index[i][j]] <= x) & (x <= last[index[i][j]])) <= pairs[index[i][j]][x] for x in range(n) for i in range(v) for j in range(i)],
        [first[index[i][j]] <= last[index[i][j]] for i in range(v) for j in range(i)],

        # implied constraint (we know the number of pairs in in each column)
        [Sum(col) == (k*(k-1)/2) for col in pairs.col],

        ## symmetry breaking
        [design[i][0] == 1 for i in range(k)],
        design[k-1][1] == 0,
        design[k][1] == 1,
    )

    return first, pairs, last, design, index, model


def solve(param):
    k = param['k']
    v = param['v']
    n = (v * (v - 1) / 2 - k * (k - 1) / 2) / (k - 1) + 1

    first, pairs, last, design, index, model = get_model(k, v, n)

    solver = model.load(param['solver'])

    solver.setHeuristic('DomainOverWDegree', 'Random', 1)
    solver.setVerbosity(param['verbose'])
    solver.setTimeLimit(param['tcutoff'])
    solver.solve()

    out = ''
    if solver.is_sat():
        out += str(design)+'\n'

        for i in range(v-1):
            for j in range(i + 1, v):
                out += str((i, j)).ljust(5) + ' ' + str(first[index[i][j]]) + ' ' + str(pairs[index[i][j]]) + ' ' + str(last[index[i][j]]) + '\n'

        the_design = [[] for y in range(n)]
        for y in range(n):
            for x in range(v):
                if design[x][y].get_value() > 0:
                    the_design[y].append(x)

        for x in range(k):
            for y in range(n):
                out += (str(the_design[y][x]+1).rjust(2) + ' ')
            out += '\n'

    out += '\nNodes: ' + str(solver.getNodes())
    return out


default = {'k': 3, 'v': 6, 'solver': 'MiniSat', 'verbose': 0, 'tcutoff': 30}


if __name__ == '__main__':
    param = input(default)
    print solve(param)
