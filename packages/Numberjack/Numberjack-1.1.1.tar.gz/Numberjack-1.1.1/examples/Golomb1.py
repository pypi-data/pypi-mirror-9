from Numberjack import *


def solve(param):
    nbMarks = param['marks']
    rulerSize = 2 ** (nbMarks - 1)

    marks = VarArray(nbMarks, rulerSize)

    model = Model(
        Minimise(Max(marks)),
        AllDiff(marks),
        AllDiff([first - second for first, second in pair_of(marks)])
    )

    solver = model.load(param['solver'])
    solver.setVerbosity(param['verbose'])
    solver.solve()

    if solver.is_sat():
        print marks
    elif solver.is_unsat():
        print "Unsatisfiable"
    else:
        print "No result returned."

    print "Nodes:", solver.getNodes()
    print "Solve time:", solver.getTime()


if __name__ == '__main__':
    default = {'solver': 'Mistral', 'verbose': 0, 'marks': 6}
    param = input(default)
    solve(param)
