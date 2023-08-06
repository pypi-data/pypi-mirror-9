from Numberjack import *


def solve(param):
    v1 = Variable(3)
    v2 = Variable(3)
    v3 = Variable(-2, 2)
    model = Model(
        v1 != v2,
        (v1 - v2) != v3,
    )

    solver = model.load(param['solver'])
    # solver.output_lp("mipneqbug.lp")
    solver.setVerbosity(param['verbose'])
    solver.setTimeLimit(param['tcutoff'])

    solver.solve()
    if solver.is_sat():
        print [v1.get_value(), v2.get_value(), v3.get_value()]


if __name__ == '__main__':
    default = {'solver': 'SCIP', 'verbose': 0, 'tcutoff': 30}
    param = input(default)
    solve(param)
