from modgrammar import *
from src.logic import *

'''
This file contains functionality for parsing expressions of FOL terms and universally quantified clauses.
 
Note that constants should start with an upper-case letter while variables should start with a lower-case one. 
Also note that symbols (names of variables, constants, functors, predicates) should not contain brackets and commas.
'''

grammar_whitespace_mode = 'optional'

delimiters = set([",", "(", ")"])
predicateCache: Dict[Tuple[str, int], Predicate] = {}
functorsCache: Dict[Tuple[str, int], Functor] = {}
varConstCache: Dict[str, Term] = {}


class Name(Grammar):
    grammar = (ANY_EXCEPT(",()"))

    def toTerm(self) -> Term:
        name = str(self.elements[0])
        if len(name) < 1:
            raise ValueError("term cannot be an empty string")

        if name[0].islower():
            return Variable(name)
        return Constant(name)


class CompTerm(Grammar):
    grammar = (Name, "(", LIST_OF(REF("Ter"), sep=","), ")")

    def toTerm(self) -> Term:
        name = str(self.elements[0])
        termsList = self.elements[2].elements
        terms = [term.toTerm() for term in termsList if str(term) not in delimiters]
        arity = len(terms)
        key = (name, arity)
        if key not in functorsCache:
            functorsCache[key] = Functor(name, arity)
        functor = functorsCache[key]
        return CompoundTerm(functor, terms)


# aka term
class Ter(Grammar):
    grammar = (Name | CompTerm)

    def toTerm(self) -> Term:
        return self.elements[0].toTerm()


# aka Literal
class Lit(Grammar):
    grammar = (Name, "(", LIST_OF(Ter, sep=","), ")")

    def toLiteral(self) -> Literal:
        name = str(self.elements[0])
        positive = True
        if name.startswith("!"):
            positive = False
            name = name[1:]

        termsList = self.elements[2].elements
        terms = [term.toTerm() for term in termsList if str(term) not in delimiters]

        arity = len(terms)
        key = (name, arity)
        if key not in predicateCache:
            predicateCache[key] = Predicate(name, arity)
        predicate = predicateCache[key]

        return Literal(Atom(predicate, terms), positive)


class ClauseGrammar(Grammar):
    grammar = (LIST_OF(Lit, sep=","))

    def toClause(self) -> Clause:
        literals = []
        if len(self.elements) > 0:
            literals = [l.toLiteral() for l in self.elements[0].elements if str(l) not in delimiters]
        return Clause(literals)


class SampleGrammar(Grammar):
    grammar = (OR(L("+"), L("-")), ClauseGrammar)

    def toSample(self) -> Tuple[bool, Iterable[Atom]]:
        return (True if "+" == str(self.elements[0]) else False, [l.atom for l in self.elements[1].toClause()])


def parseClause(string: str) -> Clause:
    '''
    Use to parse a clause.
    
    :param string: 
    :return: Clause 
    '''
    parsing = ClauseGrammar.parser()
    return parsing.parse_text(string, eof=True).toClause()


def parseLiteral(string: str) -> Literal:
    '''
    Use to parse a literal.
    :param string: 
    :return: Literal
    '''
    parsing = Lit.parser()
    return parsing.parse_text(string, eof=True).toLiteral()


def parseTerm(string: str) -> Term:
    '''
    Use to parse a term.
    :param string: 
    :return: Term 
    '''
    parsing = Ter.parser()
    return parsing.parse_text(string, eof=True).toTerm()


def parseSample(string: str) -> Tuple[bool, Iterable[Atom]]:
    '''
    Use to parse a sample, which consists of a label and an interpretation.
    :param string: 
    :return: Tuple[bool, Iterable[Atom]]
    '''
    parsing = SampleGrammar.parser()
    return parsing.parse_text(string, eof=True).toSample()
