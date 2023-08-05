#Constraining Order - a simple constraint satisfaction library
#
#Copyright (c) 2015 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
This module contains functions for solving and reducing CSPs
"""
from __future__ import unicode_literals
from itertools import product
from constrainingorder import Space
from constrainingorder.constraints import FixedValue
from constrainingorder.sets import DiscreteSet, IntervalSet

def ac3(space):
    """
    AC-3 algorithm. This reduces the domains of the variables by
    propagating constraints to ensure arc consistency.

    :param Space space: The space to reduce
    """
    #determine arcs
    arcs = {}
    for name in space.variables:
        arcs[name] = set([])
    for const in space.constraints:
        for vname1,vname2 in product(const.vnames,const.vnames):
            if vname1 != vname2:
                #this is pessimistic, we assume that each constraint
                #pairwisely couples all variables it affects
                arcs[vname1].add(vname2)

    #enforce node consistency
    for vname in space.variables:
        for const in space.constraints:
            _unary(space,const,vname)

    #assemble work list
    worklist = set([])
    for v1 in space.variables:
        for v2 in space.variables:
            for const in space.constraints:
                if _binary(space,const,v1,v2):
                    for name in arcs[v1]:
                        worklist.add((v1,name))

    #work through work list
    while worklist:
        v1,v2 = worklist.pop()
        for const in space.constraints:
            if _binary(space,const,v1,v2):
                for vname in arcs[v1]:
                    worklist.add((v1,vname))

def _unary(space,const,name):
    """
    Reduce the domain of variable name to be node-consistent with this
    constraint, i.e. remove those values for the variable that are not
    consistent with the constraint.

    returns True if the domain of name was modified
    """
    if not name in const.vnames:
        return False
    if space.variables[name].discrete:
        values = const.domains[name]
    else:
        values = const.domains[name]

    space.domains[name] = space.domains[name].intersection(values)
    return True

def _binary(space,const,name1,name2):
    """
    reduce the domain of variable name1 to be two-consistent (arc-consistent)
    with this constraint, i.e. remove those values for the variable name1,
    for which no values for name2 exist such that this pair is consistent
    with the constraint

    returns True if the domain of name1 was modified
    """
    if not (name1 in const.vnames and name2 in const.vnames):
        return False
    remove = set([])
    for v1 in space.domains[name1].iter_members():
        for v2 in space.domains[name2].iter_members():
            if const.consistent({name1 : v1, name2 : v2}):
                break
        else:
            remove.add(v1)

    if len(remove) > 0:
        if space.variables[name1].discrete:
            remove = DiscreteSet(remove)
        else:
            remove = IntervalSet.from_values(remove)

        space.domains[name1] = space.domains[name1].difference(remove)
        return True
    else:
        return False

def solve(space,method='backtrack',ordering=None):
    """
    Generator for all solutions.


    :param str method: the solution method to employ
    :param ordering: an optional parameter ordering
    :type ordering: sequence of parameter names

    Methods:

    :"backtrack": simple chronological backtracking
    :"ac-lookahead": full lookahead
    """
    if ordering is None:
        ordering = list(space.variables.keys())

    if not space.is_discrete():
        raise ValueError("Can not backtrack on non-discrete space")
    if method=='backtrack':
        for label in _backtrack(space,{},ordering):
            yield label
    elif method=='ac-lookahead':
        for label in _lookahead(space,{},ordering):
            yield label
    else:
        raise ValueError("Unknown solution method: %s" % method)


def _backtrack(space,label,ordering):
    level = len(label)
    if level == len(space.variables):
        if space.satisfied(label):
            yield label
    elif space.consistent(label):
        vname = ordering[level]
        newlabel = label.copy()
        for val in space.domains[vname].iter_members():
            newlabel[vname] = val
            for sol in _backtrack(space,newlabel,ordering):
                yield sol

def _lookahead(space,label,ordering):
    level = len(label)
    if len(label) == len(space.variables):
        if space.satisfied(label):
            yield label
    elif space.consistent(label):
        vname = ordering[level]
        var = space.variables[vname]
        newlabel = label.copy()
        for val in space.domains[vname].iter_members():
            nspace = Space(list(space.variables.values()),
                           space.constraints + [FixedValue(var,val)])
            newlabel[vname] = val
            ac3(nspace)
            for sol in _lookahead(nspace,newlabel,ordering):
                yield sol
