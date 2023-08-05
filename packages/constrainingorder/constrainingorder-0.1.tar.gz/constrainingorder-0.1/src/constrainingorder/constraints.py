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
This module defines classes describing constraints on variables
"""
from __future__ import unicode_literals
from builtins import str, object
from constrainingorder.sets import DiscreteSet, IntervalSet
from itertools import product

class Constraint(object):
    def __init__(self,domains):
        self.vnames = [v.name for v in domains.keys()]
        "Names of the variables affected by this constraint"
        self.domains = {}
        "Domains imposed by node consistency for this constraint"
        for var,dom in domains.items():
            self.domains[var.name] = dom
    def satisfied(self,lab):
        """
        check whether the labeling satisfies this constraint

        :param dict lab: A dictionary with parameter names and values
        :rtype: bool
        """
        raise NotImplementedError
    def consistent(self,lab):
        """
        check whether the labeling is consistent with this constraint

        :param dict lab: A dictionary with parameter names and values
        :rtype: bool
        """
        raise NotImplementedError

class FixedValue(Constraint):
    """
    Constraint that fixes a variable to a value
    """
    def __init__(self,variable,value):
        """
        Create a new FixedValue constraint. It enforces that a variable
        takes on a particular, fixed value.

        :param Variable variable: Variable whose value is fixed
        :param value: Value to which it is fixed
        :raises ValueError: if the value is not in the domain of the variable
        """
        if not value in variable.domain:
            raise ValueError("Value %s is incompatible with domain of %s" % 
                             (str(value),variable.name))
        if variable.discrete:
            domain = {variable : DiscreteSet([value])}
        else:
            domain = {variable : IntervalSet.from_values([value])}
        Constraint.__init__(self,domain)

        self.name = variable.name
        self.value = value

    def satisfied(self,lab):
        if self.name in lab:
            return lab[self.name] == self.value
        return False

    def consistent(self,lab):
        if self.name in lab:
            return self.satisfied(lab)
        return True

class AllDifferent(Constraint):
    """
    Constraint enforcing different values between a number of variables
    """
    def __init__(self,variables):
        """
        Create a new AllDifferent constraint. It enforces that a set of
        variable takexs on different values.

        :param sequence variables: Variables for this Constraint
        """
        Constraint.__init__(self,dict((v,v.domain) for v in variables))
    def satisfied(self,lab):
        for v1,v2 in product(self.vnames,repeat=2):
            if v1 not in lab or v2 not in lab:
                return False
            if v1 == v2:
                continue
            if lab[v1] == lab[v2]:
                return False
        return True
    def consistent(self,lab):
        for v1,v2 in product(self.vnames,repeat=2):
            if v1 not in lab or v2 not in lab or v1 == v2:
                continue
            if lab[v1] == lab[v2]:
                return False
        return True

class Domain(Constraint):
    """
    Constraint that ensures that value of a variable falls into a given
    domain
    """
    def __init__(self,variable,domain):
        """
        Create a new Domain constraint. It enforces that a variable takes on
        values from a specified set.

        :param variable: Variable whose value is restricted
        :type variable: DiscreteVariable or RealVariable
        :param domain: Set of values to which variable is restricted
        :type domain: DiscreteSet or IntervalSet
        """
        Constraint.__init__(self,{variable:domain})
    def satisfied(self,lab):
        for v in self.vnames:
            if v not in lab:
                return False
            if not lab[v] in self.domains[v]:
                return False
        return True
    def consistent(self,lab):
        for v in self.vnames:
            if v not in lab:
                continue
            if not lab[v] in self.domains[v]:
                return False
        return True

class BinaryRelation(Constraint):
    """
    Abstract Base class for constraint the describe a binary relation between
    two variables.
    """
    def __init__(self,var1,var2):
        """
        Create a new binary relation constraint between these two variables

        :param var1: The first variable
        :type var1: DiscreteVariable or RealVariable
        :param var2: The second variable
        :type var2: DiscreteVariable or RealVariable
        """
        Constraint.__init__(self,{var1:var1.domain,var2:var2.domain})
        self.v1 = var1.name
        self.v2 = var2.name
    def relation(self,val1,val2):
        """
        evaluate the relation between two values

        :param val1: The value of the first variable
        :param val2: The value of the second variable
        :rtype: bool
        """
    def satisfied(self,lab):
        for v in self.vnames:
            if v not in lab:
                return False
            elif not lab[v] in self.domains[v]:
                return False
        return self.relation(lab[self.v1],lab[self.v2])
    def consistent(self,lab):
        incomplete = False
        for v in self.vnames:
            if v not in lab:
                incomplete = True
                continue
            elif not lab[v] in self.domains[v]:
                return False
        if incomplete:
            return True
        return self.relation(lab[self.v1],lab[self.v2])

class Equal(BinaryRelation):
    """
    Equality relation
    """
    def __init__(self,var1,var2):
        BinaryRelation.__init__(self,var1,var2)
        #for equality, something can be said about the domains
        domain = var1.domain.intersection(var2.domain)
        self.domains[var1.name] = domain
        self.domains[var2.name] = domain
    def relation(self,val1,val2):
        return val1 == val2

class NonEqual(BinaryRelation):
    """
    Inequality relation
    """
    def relation(self,val1,val2):
        return val1 != val2

class Less(BinaryRelation):
    """
    Smaller-than relation
    """
    def relation(self,val1,val2):
        return val1 < val2

class LessEqual(BinaryRelation):
    """
    Smaller or equal relation
    """
    def relation(self,val1,val2):
        return val1 <= val2

class Greater(BinaryRelation):
    """
    Larger-than relation
    """
    def relation(self,val1,val2):
        return val1 > val2

class GreaterEqual(BinaryRelation):
    """
    Larger or equal relation
    """
    def relation(self,val1,val2):
        return val1 >= val2

class DiscreteBinaryRelation(Constraint):
    """
    General binary relation between discrete variables represented by the
    tuples that are in this relation
    """
    def __init__(self,var1,var2,tuples):
        """
        Create a new DiscreteBinaryRelation constraint. It restricts the values of the two variables to a set of possible combinations.


        :param var1: The first variable
        :type var1: DiscreteVariable or RealVariable
        :param var2: The second variable
        :type var2: DiscreteVariable or RealVariable
        :param tuples: The allowed value combinations
        :type tuples: sequence of tuples with values
        """
        dom1 = DiscreteSet([t[0] for t in tuples])
        dom2 = DiscreteSet([t[1] for t in tuples])
        Constraint.__init__(self,{var1:dom1,var2:dom2})
        self.v1 = var1.name
        self.v2 = var2.name
        self.tuples = tuples
    def satisfied(self,lab):
        for v in self.vnames:
            if v not in lab:
                return False
        return (lab[self.v1],lab[self.v2]) in self.tuples
    def consistent(self,lab):
        incomplete = False
        for v in self.vnames:
            if v not in lab:
                incomplete = True
                continue
            elif not lab[v] in self.domains[v]:
                return False
        if incomplete:
            return True
        return (lab[self.v1],lab[self.v2]) in self.tuples
