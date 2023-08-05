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
This module defines classes representing variables
"""
from __future__ import unicode_literals
from builtins import object
from constrainingorder.sets import DiscreteSet, IntervalSet

class Variable(object):
    """
    Abstract baseclass for variables.

    Variables describe the variables of a CSP. The instances are immutable
    and only make sense in connection with a Space.
    """
    def __init__(self,name,**kwargs):
        self.name = name
        "name of the variable"
        self.description = kwargs.get('description')
        "description of the variable"
        self.domain = None
        "domain of the variable"
        self.discrete = None
        "whether the variable is discrete or continuous"

class RealVariable(Variable):
    """
    Continuous real variable with values from the real numbers.
    """
    def __init__(self,name,**kwargs):
        """
        Create a new RealVariable

        :param str name: The name of the variable
        :param str description: An optional description of the variable
        :param IntervalSet domain: An optional domain for this variable,
                                   defaults to everything.
        """
        Variable.__init__(
            self,
            name,
            description=kwargs.get('description','')
        )

        self.domain = kwargs.get('domain',IntervalSet.everything())
        self.discrete = False

class DiscreteVariable(Variable):
    """
    Discrete variable with values from a DiscreteSet of elements.
    """
    def __init__(self,name,**kwargs):
        """
        Create a new DiscreteVariable

        :param str name: The name of the variable
        :param str description: An optional description of the variable
        :param DiscreteSet domain: An optional domain for this variable,
                                   defaults to everything.
        """
        Variable.__init__(
            self,
            name,
            description=kwargs.get('description','')
        )

        self.domain = kwargs.get('domain',DiscreteSet.everything())

        self.discrete = True
