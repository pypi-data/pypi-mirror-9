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
This module defines common stuff for constraint satisfaction probleme
"""

from __future__ import unicode_literals
from builtins import object

class Space(object):
    """
    A space is a description of the computation space for a specific CSP.
    """
    def __init__(self,variables, constraints):
        """
        Create a new Space for a CSP

        :param variables: The variables of the CSP
        :type variables: sequence of Variables
        :param constraints: The constraints of the CSP
        :type constraints: sequence of Constraints
        """
        self.constraints = constraints
        "list of constraints"
        self.variables = {}
        "dictionary of variable names to variable instances"
        self.domains = {}
        "dictionary of variable names to DiscreteSet/IntervalSet with admissible values"
        for var in variables:
            self.variables[var.name] = var
            self.domains[var.name] = var.domain

    def is_discrete(self):
        """
        Return whether this space is discrete
        """
        for domain in self.domains.values():
            if not domain.is_discrete():
                return False
        return True
    def consistent(self,lab):
        """
        Check whether the labeling is consistent with all constraints
        """
        for const in self.constraints:
            if not const.consistent(lab):
                return False
        return True
    def satisfied(self,lab):
        """
        Check whether the labeling satisfies all constraints
        """
        for const in self.constraints:
            if not const.satisfied(lab):
                return False
        return True
