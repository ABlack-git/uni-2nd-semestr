from src.logic import *
from src.folParsing import parseClause
from src.engine import *

c1 = Clause([Literal(Atom(Predicate("p", 2), [Constant("Adam"), Variable("x")]), positive=False)])
c2 = parseClause("p(Adam, fatherOf(Adam)), !p(x, fatherOf(fatherOf(x)))")
for literal in c2:
    print(
        "literal\t{}\n\thas predicate\t{}\n\tis positive\t{}\nand arguments...".format(literal, literal.atom.predicate,
                                                                                       literal.positive))
    for term in literal:
        if isinstance(term, CompoundTerm):
            print("\tcompound term\t{}\n\t\twith function symbol\t{}".format(term, term.functor))
    for argument in term:
        print("\t\t{}".format(argument))
    else:
        print("\t{}\t{}".format(term.__class__, term))

c3 = parseClause("siblings(x,y,z,w)")
x = Variable("x")
y = Variable("y")
z = Variable("z")
issac = Constant("Issac")
kain = Constant("Kain")
substitution = {x: issac, y: kain, z: x}
substitutedClause = c3.substitute(substitution)
print("original clause\t{}\nsubstituted clause\t{}".format(c3, substitutedClause))

c4 = parseClause("p(x,y)")
c5 = parseClause("p(z,w)")
c4SubsumesC5 = subsumes(c4, c5)
print("{}\t{}\t{}".format(c4, "theta-subsumes" if c4SubsumesC5 else "does not theta-subsume", c5))
c5SubsumesC4 = subsumes(c5, c4)
print("{}\t{}\t{}".format(c5, "theta-subsumes" if c5SubsumesC4 else "does not theta-subsume", c4))

c6 = parseClause("p(A, x, f(x))")
c7 = parseClause("p(y, f(B), f(f(B))), p(x,z,u)")
print("lgg of\n\t{}\n\t{}\n\tis\t{}".format(c6, c7, lgg(c6, c7, reduceResult=True)))
c8 = parseClause("p(A, x, x)")
c9 = parseClause("p(y, B, A), p(z, x, u)")
print("lgg of\n\t{}\n\t{}\n\tis\t{}".format(c8, c9, lgg(c8, c9, reduceResult=True)))

rules = [parseClause("!edge(x,y), edge(y,x)")]
graph = [literal.atom for literal in parseClause("edge(1,2), edge(2,3), edge(4,3)")]
extendedGraph = leastHerbrandModel(rules, graph)
print("The least Herbrand model of given rules and data is\t{}".format(", ".join(str(a) for a in extendedGraph)))

sum_rule = parseClause("greater(sum(x1,x2), sum(k1,k2)), equals(sum(x1,x2), sum(k1,k2))")
obs = parseClause("equals(sum(x1,x2), sum(k1,k2))")
obs2 = parseClause("!greater(sum(x1,x2), sum(k1,k2)), equals(sum(x1,x2), sum(k1,k2))")
print(subsumes(sum_rule, obs))

a1 = parseClause('P(sum(val(X1), val(X1), val(X3)), sum(val(Y1), val(Y2), val(Y3))), P1_Cards(X1,X1,X3)')
a2 = parseClause('P(sum(val(Z1), val(Z2), val(Z3)), sum(val(G1), val(G2), val(G3))), P1_Cards(Z1, Z2, Z3)')
lgg1 = lgg(a1, a2)
print(lgg1)
a3 = parseClause('P(sum(val(X1), val(X3), val(X3)), sum(val(Y1), val(Y2), val(Y3)))')
a4 = parseClause('P(sum(val(x1), val(x2), val(x3)), sum(val(y1), val(y2), val(y3)))')
print(subsumes(Clause([]), a3))
# lgg2 = lgg(lgg1, a3)
# print(lgg2)
# print(subsumes(lgg2, a1))
