from typing import Set, Iterable, Tuple, Dict, Iterator
import functools

'''
This file contains various support for first-order predicate (FOL) logic.

Note that constants should start with an upper-case letter while variables should start with a lower-case one. 
Also note that symbols (names of variables, constants, functors, predicates) should not contain brackets and commas.
'''


def unionSets(iterableOfSets: Iterable[Set['Generic']]) -> Set['Generic']:
    '''
    Taking iterable of set, this method makes one big set by union of all the set given.

    :type iterableOfSets: iterable of set of T
    :rtype: set of T
    '''
    iterableOfSets = tuple(iterableOfSets)
    if len(iterableOfSets) == 1:
        # special case, trailing comma at the end of the tuple makes the problem
        return iterableOfSets[0]
    try:
        if len(iterableOfSets) <= 0:
            return set()
        return functools.reduce(lambda x, y: x.union(y), iterableOfSets)
    except Exception as e:
        raise ValueError('unionSets: {}\n{}'.format(iterableOfSets, e))


class Term:
    '''
    An interface for FOL term.
    '''

    def getVariables(self) -> Set['Variable']:
        '''
        Returns set of the term's variables.

        :rtype: set of Variable
        '''
        raise NotImplementedError("Method not implemented.")

    def getConstants(self) -> Set['Constant']:
        '''
        Returns set of constants of the term.

        :rtype: set of Constant
        '''
        raise NotImplementedError("Method not implemented.")

    def substitute(self, substitution: Dict['Variable', 'Term']) -> 'Term':
        '''
        Returns the same term but substituted by the substitution represented by dict of (Variable,Term).

        :type substitution: dict of (Variable,Term)
        :rtype: Term
        '''
        raise NotImplementedError("Method not implemented.")

    def getFunctors(self) -> Set['Functor']:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        raise NotImplementedError("Method not implemented.")


class Variable(Term):
    '''
    Represents FOL variable.
    '''

    def __init__(self, name: str):
        self.name: str = name

    def __hash__(self):
        return hash(str(self.name))

    def __str__(self):
        return self.name

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and str(self) == str(o)

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def getVariables(self) -> Set['Variable']:
        '''
        Returns set of the term's variables.

        :rtype: set of Variable
        '''
        r = set()
        r.add(self)
        return r

    def substitute(self, substitution: Dict['Variable', Term]) -> Term:
        '''
        Returns the same term but substituted by the substitution represented by dict of (Variable,Term).

        :type substitution: dict of (Variable,Term)
        :rtype: Term
        '''
        if self in substitution:
            return substitution[self]
        return self

    def getConstants(self) -> Set['Constant']:
        '''
        Returns set of constants of the term.

        :rtype: set of Constant
        '''
        return set()

    def getFunctors(self) -> Set['Functor']:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        return set()


class Constant(Term):
    '''
    Represents FOL constant.
    '''

    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(str(self))

    def getVariables(self) -> Set[Variable]:
        '''
        Returns set of the term's variables.

        :rtype: set of Variable
        '''
        return set()

    def substitute(self, substitution: Dict[Variable, Term]) -> Term:
        '''
        Returns the same term but substituted by the substitution represented by dict of (Variable,Term).

        :type substitution: dict of (Variable,Term)
        :rtype: Term
        '''
        return self

    def getConstants(self) -> Set['Constant']:
        '''
        Returns set of constants of the term.

        :rtype: set of Constant
        '''
        r = set()
        r.add(self)
        return r

    def getFunctors(self) -> Set['Functor']:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        return set()


class Functor:
    '''
    Represents FOL functor.
    '''

    def __init__(self, name: str, arity: int):
        self.name: str = name
        self.arity: int = arity

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name and self.arity == other.arity

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return (self.name, self.arity).__hash__()

    def __str__(self):
        return "{}/{}".format(self.name, self.arity)


class CompoundTerm(Term):
    '''
    Use .functor to get Functor of this composed term.
    Use .terms to get tuple of terms.
    '''

    def __init__(self, functor: Functor, terms: Iterable[Term]):
        '''
        Creates and returns a new compound term which is constructed by a functor applied to list of arguments.

        :type functor: Functor
        :type terms: iterable of Term   
        :rtype: CompoundTerm
        '''
        terms = tuple(terms)
        if functor.arity != len(terms):
            raise ValueError(
                "functor's arity '{}' is different than arguments given '{}'".format(functor,
                                                                                     ', '.join(map(str, terms))))
        self.functor: Functor = functor
        self.terms: Tuple[Term] = terms

    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(self).__eq__(str(other))

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return str(self).__hash__()

    def __str__(self):
        if len(self.terms) != self.functor.arity:
            raise AssertionError()
        return "{}({})".format(self.functor.name, ", ".join(map(str, self.terms)))

    def __iter__(self) -> Iterator[Term]:
        return iter(self.terms)

    def __getitem__(self, idx) -> Term:
        return self.terms[idx]

    def __len__(self):
        return len(self.terms)

    def getVariables(self) -> Set[Variable]:
        '''
        Returns set of the term's variables.

        :rtype: set of Variable
        '''
        return unionSets(term.getVariables() for term in self.terms)

    def substitute(self, substitution: Dict[Variable, Term]) -> Term:
        '''
        Returns the same term but substituted by the substitution represented by dict of (Variable,Term).

        :type substitution: dict of (Variable,Term)
        :rtype: Term
        '''
        return CompoundTerm(self.functor, [term.substitute(substitution) for term in self.terms])

    def getConstants(self) -> Set[Constant]:
        '''
        Returns set of constants of the term.

        :rtype: set of Constant
        '''
        return unionSets(term.getConstants() for term in self.terms)

    def getFunctors(self) -> Set[Functor]:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        result = set()
        result.add(self.functor)
        result = result.union(unionSets(map(lambda term: term.getFunctors(), self.terms)))
        return result


class Predicate:
    def __init__(self, name: str, arity: int):
        '''
        Creates and returns a new predicate by given name and arity. Length of the name should be longer than zero.

        :param name: str
        :param arity: int,>=0
        :rtype: Predicate
        '''
        self.name: str = name
        self.arity: int = arity

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name and self.arity == other.arity

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return (self.name, self.arity).__hash__()

    def __str__(self):
        '''
        Get Prolog-like notation.

        :rtype: str
        '''
        return "{}/{}".format(self.name, self.arity)


class Atom:
    def __init__(self, predicate: Predicate, terms: Iterable[Term]) -> 'Atom':
        '''
        Creates new atom given predicate and list of terms.

        :type predicate: Predicate
        :type terms: list of Term
        :rtype: Atom
        '''
        terms = tuple(terms)
        if isinstance(predicate, Predicate) and predicate.arity != len(terms):
            raise ValueError(
                "predicate's '{}' arity differs from the arguments given '{}'".format(predicate,
                                                                                      ', '.join(map(str, terms))))
        self.predicate: Predicate = predicate if isinstance(predicate, Predicate) else Predicate(predicate.name, len(terms))
        self.terms: Tuple[Term] = terms
        self.arity: int = predicate.arity

    def __str__(self):
        if 1 > self.arity:
            return self.predicate.name
        return "{}({})".format(self.predicate.name, ", ".join(map(str, self.terms)))

    # just lexical comparison
    def __eq__(self, other):
        return isinstance(other, Atom) and str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __iter__(self) -> Iterator[Term]:
        return iter(self.terms)

    def __getitem__(self, idx) -> Term:
        return self.terms[idx]

    def __len__(self):
        return len(self.terms)

    def getVariables(self) -> Set[Variable]:
        '''
        Returns set of variables in the atom.

        :rtype: set of Variable
        '''
        return unionSets(term.getVariables() for term in self.terms)

    def substitute(self, substitution: Dict[Variable, Term]) -> 'Atom':
        '''
        Returns new atom obtained by applying the substitution on this atom.

        :type substitution: dict of (Variable,Term)
        :rtype: Atom
        '''
        return Atom(self.predicate, [term.substitute(substitution) for term in self.terms])

    def isGround(self) -> bool:
        '''
        Returns true iff the atom is ground.

        :rtype: bool
        '''
        return len(self.getVariables()) < 1

    def getConstants(self) -> Set[Constant]:
        '''
        Returns set of constants of the atom.

        :rtype: set of Constant
        '''
        return unionSets(term.getConstants() for term in self.terms)

    def getFunctors(self) -> Set[Functor]:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        return unionSets(map(lambda term: term.getFunctors(), self.terms))


class Literal:
    def __init__(self, atom: Atom, positive: bool = True):
        '''
        Creates and returns a new literal from the atom. The literal is negation of the atom if positive is set to False.

        :type atom: Atom
        :type positive: bool
        :rtype: Literal
        '''
        self.atom: Atom = atom
        self.positive: bool = positive

    def __str__(self):
        return "{}{}".format("" if self.positive else "!", str(self.atom))

    # just lexical comparison
    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __iter__(self) -> Iterator[Atom]:
        return iter(self.atom)

    def __getitem__(self, idx) -> Term:
        return self.atom[idx]

    def __len__(self):
        return len(self.atom)

    def negation(self) -> "Literal":
        return Literal(self.atom, not self.positive)

    def getPredicate(self) -> Predicate:
        '''
        Return the predicate.

        :rtype: Predicate
        '''
        return self.atom.predicate

    def getVariables(self) -> Set[Variable]:
        '''
        Returns variables in the literal.

        :rtype: set of Variable
        '''
        return self.atom.getVariables()

    def substitute(self, substitution: Dict[Variable, Term]) -> 'Literal':
        '''
        Returns new literal obtained by applying the substitution on itself.

        :type substitution: dict of (Variable,Term)
        :rtype: Literal
        '''
        return Literal(self.atom.substitute(substitution), positive=self.positive)

    def isGround(self) -> bool:
        '''
        Returns true iff the atom is ground.

        :rtype: bool
        '''
        return self.atom.isGround()

    def getConstants(self) -> Set[Constant]:
        '''
        Returns set of constants of the literal.

        :rtype: set of Constant
        '''
        return self.atom.getConstants()

    def getFunctors(self) -> Set[Functor]:
        '''
        Returns set of functors.

        :rtype: set of Functor
        '''
        return self.atom.getFunctors()


class Clause(Iterable[Literal]):
    def __init__(self, literals: Iterable[Literal]):
        '''
        Creates a clause given the list of literals.

        :type literals: iterable of Literal
        :rtype: Clause
        '''
        lits = set()
        for l in literals:
            lits.add(l)
        tup = tuple(lits)

        self.literals: Tuple[Literal] = tup

    def __str__(self, endingDot=False):
        '''
        Set endingDot to True if you want to obtain string description of the clause with an ending dot.

        :type endingDot: bool
        :rtype: str
        '''
        if not self.literals:
            return "{{}}{}".format("." if endingDot else "")
        return '{}{}'.format(
            ' , '.join(sorted(map(str, self.literals))),
            "." if endingDot else "")

    # just lexical comparison
    def __eq__(self, other):
        return isinstance(other, self.__class__) and str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __iter__(self) -> Iterator[Literal]:
        return iter(self.literals)

    def __len__(self):
        return len(self.literals)

    def getPredicates(self) -> Set[Predicate]:
        '''
        Returns set of predicates in the clause.

        :rtype: set of Predicate
        '''
        return set(literal.getPredicate() for literal in self.literals)

    def getVariables(self) -> Set[Variable]:
        '''
        Returns set of variables in the clause.

        :rtype: set of Variable
        '''
        if not self.literals:
            return set()
        return unionSets(literal.getVariables() for literal in self.literals)

    def append(self, literal) -> 'Clause':
        '''
        Creates and returns a new clause by appending the given literal to the set of literals of this clause.

        :type literal: Literal
        :rtype: Clause
        '''
        literals = set(literal for literal in self.literals)
        literals.add(literal)
        return Clause(literals)

    def extend(self, literals: Iterable[Literal]) -> 'Clause':
        '''
        Creates and returns a new clause by appending the given literal to the set of literals of this clause.

        :type literal: Literal
        :rtype: Clause
        '''
        original = set(literal for literal in self.literals)
        original = original.union(literals)
        return Clause(original)

    def substitute(self, substitution: Dict[Variable, Term]) -> Term:
        '''
        Returns new clause by applying the substitution on itself.

        :type substitution: dict of (Variable,Term)
        :rtype: Clause
        '''
        return Clause(literal.substitute(substitution) for literal in self.literals)

    def getNumberOfLiterals(self) -> int:
        return len(self.literals)

    def isGround(self) -> bool:
        '''
        Returns true iff the clause is ground.

        :rtype: bool
        '''
        return all(literal.isGround() for literal in self.literals)

    def flipSings(self):
        return Clause(l.negation() for l in self)


def unifyTermFirstWithSecond(first: Term, second: Term, mapping: Dict[Variable, Term] = None) -> Dict[Variable, Term]:
    '''
    Returns substitution which such that when applied to the first term it returns the second one. Returns None if such unification does not exists.

    :param first: Term
    :param second: Term
    :return: Dict[Variable,Term] 
    '''
    if None is mapping:
        mapping = {}

    if isinstance(first, Constant):
        # here, we need to add type restriction if it is introduced in the framework
        if not (isinstance(second, Constant) and first == second):
            return None
    elif isinstance(first, Variable):
        # here, we need to add type restriction if it is introduced in the framework
        if first in mapping and mapping[first] != second:
            return None
        else:
            mapping[first] = second
    elif isinstance(first, CompoundTerm) and isinstance(second, CompoundTerm) and first.functor == second.functor and len(first) == len(second):
        for t1, t2 in zip(first, second):
            mapping = unifyTermFirstWithSecond(t1, t2, mapping)
            if None is mapping:
                return None
    else:
        return None
    return mapping


def unifyFirstWithSecond(first: Literal, second: Literal) -> Dict[Variable, Term]:
    '''
    Returns substitution which such that when applied to the first literal it returns the second one. Returns None if such unification does not exists. It does not care about sings of the literals.
    
    :param first: Literal
    :param second: Literal
    :return: Dict[Variable,Term] 
    '''
    # better be save than sorry
    if second.getPredicate() != first.getPredicate() or len(second) != len(first):
        raise ValueError("Predicates of these two terms are not equal:\t'{}',\t{}".format(first.getPredicate(), second.getPredicate()))
    mapping: Dict[Variable, Term] = {}
    for t1, t2 in zip(first, second):
        mapping = unifyTermFirstWithSecond(t1, t2, mapping)
        if None is mapping:
            return None
    return mapping


def isDefiniteClause(clause: Clause) -> bool:
    return 1 == len([l for l in clause if l.positive])


def isRangeRestricted(clause: Clause) -> bool:
    positiveLiterals = Clause(l for l in clause if l.positive)
    if 0 == len(positiveLiterals):
        return True
    negativeLiterals = Clause(l for l in clause if not l.positive)
    if 0 == len(negativeLiterals):
        return False
    return positiveLiterals.getVariables().issubset(negativeLiterals.getVariables())
