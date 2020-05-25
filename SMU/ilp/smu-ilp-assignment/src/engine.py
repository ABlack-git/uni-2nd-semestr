import itertools
import pycosat
import time
from collections import defaultdict
from typing import Callable, Collection, List, Set, Dict
from src.logic import *


def addSpecialSymbol(literal: Literal) -> Literal:
    prefix = "~~" if literal.positive else "~~!"
    predicate = Predicate(prefix + literal.atom.predicate.name, literal.atom.predicate.arity)
    return Literal(Atom(predicate, literal.atom.terms), positive=True)


def addExactlyOneHoldConstraint(constraints: List[List[int]], variables: Iterable[int]) -> None:
    constraints.append([variable for variable in variables])
    for i, j in itertools.combinations(variables, r=2):
        constraints.append([-i, -j])


def findPycosatSubstitutions(allSolutions: bool, query: Iterable[Literal], world: Iterable[Literal]) -> List[Dict[Variable, Term]]:
    # general case
    start = time.time()
    # encode to CSP

    # encode instance
    literalsPerPredicate: Dict[Predicate, Set[Literal]] = defaultdict(set)
    totalVars = 0

    terms: Iterable[Term] = unionSets(set(literal.atom.terms) for literal in world)
    universalDomain: Set[Variable] = set()

    def varCounter():
        nonlocal totalVars
        totalVars += 1
        return totalVars

    assignments: Dict['var', Dict['term', int]] = defaultdict(lambda: defaultdict(varCounter))  # id of var->term, i.e. assignment[var][term] returns id of propositional variable
    for literal in world:
        literalsPerPredicate[literal.getPredicate()].add(literal)
        if not literal.positive:
            raise ValueError("Only non-negated literals are allowed for the world variable.")

    constraints: List[List[int]] = []
    for literal in query:
        if literal.isGround():
            if (literal.positive and literal not in world) or ((not literal.positive) and literal.negation() in world):
                return []  # if a query's l is ground but is not in the world, then the query cannot subsume the world (similarly for negative literal)
            continue

        if not literal.positive:
            for variable in literal.getVariables():
                universalDomain.add(variable)

        possibleMappings: Set[Tuple[int]] = set()
        for potential in literalsPerPredicate[literal.getPredicate()]:
            possibleUnification = unifyFirstWithSecond(literal, potential)
            if None is possibleUnification:
                continue
            possibleMappings.add(tuple(assignments[var][target] for var, target in possibleUnification.items()))

        if literal.positive and not possibleMappings:  # there is no literal in world to which l can be mapped, therefore unsatisfiable
            return []

        if literal.positive:
            mappingVariants = []
            for mapping in possibleMappings:
                auxiliarLiteralVariable = varCounter()
                mappingVariants.append(auxiliarLiteralVariable)
                implication = [-propositionalVariable for propositionalVariable in mapping]
                implication.append(auxiliarLiteralVariable)
                constraints.append(implication)
                for propositionalVariable in mapping:
                    constraints.append([propositionalVariable, -auxiliarLiteralVariable])
            addExactlyOneHoldConstraint(constraints, mappingVariants)
        else:  # actually restriction on solutions
            for forbidden in possibleMappings:
                constraints.append([-propositionalVariable for propositionalVariable in forbidden])

    for variable, term in itertools.product(universalDomain, terms):
        addingPropositionalVariable = assignments[variable][term]

    for var, termsAssignment in assignments.items():
        addExactlyOneHoldConstraint(constraints, termsAssignment.values())

    encodingTime = time.time() - start
    # solver
    start = time.time()
    solutions = []
    if allSolutions:
        for solution in pycosat.itersolve(constraints):
            if solution not in ("UNSAT", "UNKNOWN"):
                solutions.append(solution)
    else:
        solution = pycosat.solve(constraints)
        if solution not in ("UNSAT", "UNKNOWN"):
            solutions.append(solution)

    satTime = time.time() - start
    # print("encoding\t{}\nsat     \t{}".format(encodingTime, satTime))
    # transfer solution to FOL representation
    propositionalToAssignment = {propositionalVariable: (variable, term) for variable, termsAssignment in assignments.items() for term, propositionalVariable in termsAssignment.items()}
    substitutions = [dict(propositionalToAssignment[propositionalVariable] for propositionalVariable in model if propositionalVariable in propositionalToAssignment) for model in solutions]
    return substitutions


def findSubstitutions(query: Clause, world: Clause, allSolutions=True) -> List[Dict[Variable, Term]]:
    '''
    By default it search for all substitutions (all_solutions=True). If all_solutions=False, then only one is returned.

    :param query: Clause
    :param world: Clause
    :param allSolutions: bool 
    :return: List[Dict[Variable,Term]]
    '''

    # special (ground) case
    if len(query.getVariables()) < 1:
        for l in query:
            if (l.positive and l not in world) or ((not l.positive) and l.negation() in world):
                return []
        return [{}]  # although it looks weird, it actually means that there is one empty substitution, i.e. a very trivial one

    return findPycosatSubstitutions(allSolutions, query, world)


def subsumes(query: Clause, world: Clause) -> bool:
    '''
    Given a world and a query, the method decides whether the query theta-subsume the world.
    :param query: Clause 
    :param world: Clause
    :return: bool
    '''
    query = Clause(map(addSpecialSymbol, query))
    world = Clause(map(addSpecialSymbol, world))

    substitutions = findSubstitutions(query, world, allSolutions=False)
    return len(substitutions) > 0


def getHead(clause: Clause, polarity=True) -> Literal:
    '''
    Returns the only literal with given polarity. If no such literal is presented, it raises an exception.
    
    :param clause: Clause
    :param polarity: bool
    :return: Literal 
    '''
    positiveLiterals = list(l for l in clause if polarity == l.positive)
    if len(positiveLiterals) != 1:
        raise ValueError()
    return positiveLiterals[0]


def leastHerbrandModel(rules: Collection[Clause], world: Collection[Atom]) -> Iterable[Atom]:
    '''
    Given an iterable of definite range-restricted clauses and a world, i.e. list of true facts, it returns the least Herbrand model, i.e. all positive literals that derived from the input parameters.
     
    :param rules: Collection[Clause]
    :param world: Iterable[Atom]
    :return: Clause
    '''
    for rule in rules:
        if (not isRangeRestricted(rule)) or (not isDefiniteClause(rule)):
            raise ValueError("LeastHerbrandModel generator handles only definite range-restricted clauses.")

    existentiallyQuantifiedDefiniteRules: Set[Tuple[Clause, Literal]] = set()
    for clause in rules:
        if isDefiniteClause(clause):
            existentiallyQuantifiedDefiniteRules.add((clause.flipSings(), getHead(clause, polarity=True)))
        else:
            raise ValueError("This method takes only definite rules, but given\t{}".format(clause))
    facts: Clause = Clause([Literal(a) for a in world])
    change = True
    while change:
        change = False
        for c, head in existentiallyQuantifiedDefiniteRules:
            substitutions = findSubstitutions(c, facts)
            change |= len(substitutions) > 0
            facts = facts.extend([head.substitute(s) for s in substitutions])

    return [literal.atom for literal in facts]


def reduce(clause: Clause) -> Clause:
    '''
    Returns a reduced clause for the given one.
    
    :param clause: Clause
    :return: Clause 
    '''
    reduced = clause
    for literal in clause:
        if literal not in reduced:
            continue  # speeding-up hack
        shorther = Clause(l for l in reduced if l != literal)
        if subsumes(reduced, shorther):
            reduced = shorther
    return reduced


def lggByTaxonomic(t1: Constant, t2: Constant, antiunifier: Callable[[Term, Term], Term]) -> Term:
    # if the two input constants are the same, then returns the constant
    # if they have common lowest common ancestor, then it is returned
    # else it returns a variable
    if t1 == t2:
        return t1
    # place for taxonomical information insertion
    return antiunifier(t1, t2)


def lggTerms(t1: Term, t2: Term, antiunifier: Callable[[Term, Term], Term]) -> Term:
    if isinstance(t1, Constant) or isinstance(t2, Constant):
        return lggByTaxonomic(t1, t2, antiunifier)
    if isinstance(t1, CompoundTerm) and isinstance(t2, CompoundTerm) and t1.functor == t2.functor:
        return CompoundTerm(t1.functor,
                            (lggTerms(it1, it2, antiunifier) for it1, it2 in zip(t1.terms, t2.terms)))
    return antiunifier(t1, t2)


def lgg(alpha: Clause, beta: Clause, reduceResult: bool = True) -> Clause:
    '''
    Returns (reduced) lgg of clauses alpha and beta and reduces.
    
    :param alpha: Clause
    :param beta: Clause
    :param reduceResult: bool 
    :return: Clause 
    '''
    cache = {}

    def antiunifier(t1: Term, t2: Term) -> Term:
        if isinstance(t1, Constant) and t1 == t2:
            return t1
        key = (t1, t2)
        if key not in cache:
            cache[key] = Variable("v" + str(len(cache)))  # well, this should be parametrized by constVar or varConst parameter :))
        return cache[key]

    general = Clause(
        Literal(Atom(l1.getPredicate(), (lggTerms(t1, t2, antiunifier) for t1, t2 in zip(l1.atom.terms, l2.atom.terms))), positive=l1.positive)
        for l1, l2 in itertools.product(alpha, beta) if
        l1.getPredicate() == l2.getPredicate() and l1.positive == l2.positive)

    if reduceResult:
        general = reduce(general)
    return general
