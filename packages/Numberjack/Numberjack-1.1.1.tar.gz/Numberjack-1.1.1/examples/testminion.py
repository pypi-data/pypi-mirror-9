from Numberjack import *


if __name__ == '__main__':
    m = Model()
    vs = VarArray(5, 1, 5)
    v1 = Variable(5)
    v2 = Variable(5)
    # m += AllDiff([v1, v2])
    m += AllDiff(vs)
    # m += v1 == v2 / 2
    m += v1 == v2 * 2
    # m += v1 == 0
    # m += Variable([2, 4, 6])
    # m += Variable(5) != 3
    # m += Variable(3) != Variable(4)
    # m += AllDiff(VarArray(5, 5))
    # m += Variable(3) == Abs(Variable(-3, 3))
    # m += Abs(Variable(-3, 3)) == Variable(3)
    # m += Variable(5) == Variable([2, 4, 6, 8]) / Variable(1, 2)
    # m += Variable(10) == Element(VarArray(5, 5), Variable(3))
    # m += Gcc(VarArray(3, 1, 3), {1: [0, 1], 2: [0, 1], 3: [3, 3]})
    # m += Variable(5) < Variable(5)
    # m += Variable(5) <= Variable(5)
    # m += Variable(5) > Variable(5)
    # m += Variable(5) >= Variable(5)
    # m += LeqLex(VarArray(5, 5), VarArray(5, 5))
    # m += LessLex(VarArray(5, 5), VarArray(5, 5)) # print m
    # m += v2 == Element(vs, v1)
    # s = m.load("Minion", vs)
    s = m.load("Minion")
    s.setVerbosity(1)
    s.solve()
    print s.is_sat(), s.is_unsat()
    if s.is_sat():
        print vs, v1, v2
