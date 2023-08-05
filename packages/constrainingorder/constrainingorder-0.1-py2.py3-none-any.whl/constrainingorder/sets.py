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
This module defines datastructures to represent discrete and real sets in one
and more dimensions
"""
from __future__ import unicode_literals
from builtins import zip, next, str, object
from itertools import tee,product

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class Interval(object):
    """
    An interval on the real axis.
    """
    def __init__(self,bounds,included):
        """
        Create a new Interval with bounds. If the right bound is larger than
        the left bound, the interval is assumed to be empty.

        :param sequence bounds: left and right bounds
        :param sequence included: bools indicating whether the bounds are
                                  included in the interval.
        """
        self.bounds = tuple(bounds)
        self.included = tuple(included)

    @classmethod
    def everything(cls):
        """
        Create a new Interval representing the full real axis
        """
        return cls((-float("inf"),float("inf")),(True,True))

    @classmethod
    def from_value(cls,value):
        """
        Create a new Interval representing a single real number.

        :param float value: The member of the Interval
        """
        return cls((value,value),(True,True))

    @classmethod
    def open(cls,a,b):
        """
        Create a new open Interval.

        :param float a: Left bound
        :param float b: Right bound
        """
        return cls((a,b),(False,False))

    @classmethod
    def closed(cls,a,b):
        """
        Create a new closed Interval.

        :param float a: Left bound
        :param float b: Right bound
        """
        return cls((a,b),(True,True))

    @classmethod
    def leftopen(cls,a,b):
        """
        Create a new halfopen Interval (left bound is excluded, right bound
        included).

        :param float a: Left bound
        :param float b: Right bound
        """
        return cls((a,b),(False,True))

    @classmethod
    def rightopen(cls,a,b):
        """
        Create a new halfopen Interval (right bound is excluded, left bound
        included).

        :param float a: Left bound
        :param float b: Right bound
        """
        return cls((a,b),(True,False))

    def is_disjoint(self,other):
        """
        Check whether two Intervals are disjoint.

        :param Interval other: The Interval to check disjointedness with.
        """
        if self.is_empty() or other.is_empty():
            return True

        if self.bounds[0] < other.bounds[0]:
            i1,i2 = self,other
        elif self.bounds[0] > other.bounds[0]:
            i2,i1 = self,other
        else:
            #coincident lower bounds
            if self.is_discrete() and not other.included[0]:
                return True
            elif other.is_discrete() and not self.included[0]:
                return True
            else:
                return False

        return not i2.bounds[0] in i1

    def _difference(self,other):
        #the set of intervals is not closed w.r.t the difference, as it might
        #yield zeor,one or two intervals as a result. Therefore this method
        #is only used as a utility function for IntervalSet.

        if self.is_empty():
            return []

        if other.is_empty() or self.is_disjoint(other):
            return [self]

        b1 = (self.bounds[0],other.bounds[0])
        i1 = (self.included[0],not other.included[0])
        int1 = Interval(b1,i1)

        b2 = (other.bounds[1],self.bounds[1])
        i2 = (not other.included[1],self.included[1])
        int2 = Interval(b2,i2)

        if other.bounds[0] in self and other.bounds[1] in self:
            #-------
            # ***
            return [int1,int2]

        elif other.bounds[0] in self:
            bounds = (self.bounds[0],other.bounds[0])
            include = (self.included[0],not other.included[0])
            #-------
            # *********
            return [int1]
        elif other.bounds[1] in self:
            #    -------
            #*******
            return [int2]
        else:
            raise RuntimeError("This should not happen")

    def _union(self,other):
        #the set of intervals is not closed w.r.t the union, as it might
        #yield one or two intervals as a result. Therefore this method
        #is only used as a utility function for IntervalSet.

        if self.is_empty() and other.is_empty():
            return []
        elif self.is_empty():
            return [other]
        elif other.is_empty():
            return [self]

        if self.bounds[0] < other.bounds[0]:
            i1,i2 = self,other
        elif self.bounds[0] > other.bounds[0]:
            i2,i1 = self,other
        else:
            if self.included[0]:
                i1,i2 = self,other
            else:
                i2,i1 = self,other

        if i1.is_disjoint(i2):
            return [i1,i2]
        elif i2.bounds[0] in i1 and i2.bounds[1] in i1:
            #-------
            # ***
            return [i1]
        elif i2.bounds[0] in i1:
            bounds = (i1.bounds[0],i2.bounds[1])
            include = (i1.included[0],i2.included[1])
            #-------
            # *********
            return [Interval(bounds,include)]
        else:
            raise RuntimeError("This should not happen")

    def intersection(self,other):
        """
        Return a new Interval with the intersection of the two intervals,
        i.e.  all elements that are in both self and other.

        :param Interval other: Interval to intersect with
        :rtype: Interval
        """
        if self.bounds[0] < other.bounds[0]:
            i1,i2 = self,other
        else:
            i2,i1 = self,other

        if self.is_disjoint(other):
            return Interval((1,0),(True,True))

        bounds = [None,None]
        included = [None,None]
        #sets are not disjoint, so i2.bounds[0] in i1:
        bounds[0] = i2.bounds[0]
        included[0] = i2.included[0]

        if i2.bounds[1] in i1:
            bounds[1] = i2.bounds[1]
            included[1] = i2.included[1]
        else:
            bounds[1] = i1.bounds[1]
            included[1] = i1.included[1]

        return Interval(bounds,included)

    def is_empty(self):
        """
        Check whether this interval is empty.

        :rtype: bool
        """
        if self.bounds[1] < self.bounds[0]:
            return True
        if self.bounds[1] == self.bounds[0]:
            return not (self.included[0] and self.included[1])

    def is_discrete(self):
        """
        Check whether this interval contains exactly one number

        :rtype: bool
        """
        return self.bounds[1] == self.bounds[0] and\
               self.included == (True,True)

    def get_point(self):
        """
        Return the number contained in this interval.

        :rtype: float
        :raises ValueError: if Interval contains more than exactly one number.
        """
        if not self.is_discrete():
            raise ValueError("Interval doesn't contain exactly one value")
        return self.bounds[0]

    def __contains__(self,x):
        """
        Check membership of the element.

        :param float x: Element to check membership of
        :rtype: bool
        """
        if self.is_empty():
            return False
        if self.included[0]:
            if not (x >= self.bounds[0]):
                return False
        else:
            if not (x > self.bounds[0]):
                return False
        if self.included[1]:
            if not (x <= self.bounds[1]):
                return False
        else:
            if not (x < self.bounds[1]):
                return False
        return True

    def __repr__(self):
        if self.is_empty():
            return "Interval((1,0),(False,False))"
        return "Interval(%s,%s)" % (self.bounds,self.included)

    def __str__(self):
        if self.is_empty():
            return "<empty set>"
        else:
            left = ["(","["]
            right = [")","]"]

            bnd = "%s,%s" % self.bounds
            brk = (left[self.included[0]],right[self.included[1]])

            return "%s%s%s" % (brk[0],bnd,brk[1])

class IntervalSet(object):
    """
    A set of intervals to represent quite general sets in R
    """
    def __init__(self,ints):
        """
        Create a new IntervalSet.

        :param sequence ints: Intervals for this IntervalSet
        """
        self.ints = []
        for i in sorted(ints,key=lambda x: x.bounds[0]):
            if i.is_empty():
                continue
            if len(self.ints) > 0 and not i.is_disjoint(self.ints[-1]):
                i2 = self.ints.pop(-1)
                self.ints.extend(i2._union(i))
            else:
                self.ints.append(i)

        for i1,i2 in pairwise(self.ints):
            if not i1.is_disjoint(i2):
                raise ValueError('Intervals are not disjoint')

    @classmethod
    def everything(cls):
        """
        Create a new IntervalSet representing the full real axis.
        """
        return cls([Interval.everything()])

    @classmethod
    def from_values(cls,values):
        """
        Create a new IntervalSet representing a set of isolated real numbers.

        :param sequence values: The values for this IntervalSet
        """
        return cls([Interval.from_value(v) for v in values])

    def is_empty(self):
        """
        Check whether this IntervalSet is empty.

        :rtype: bool
        """
        return len(self.ints) == 0

    def is_discrete(self):
        """
        Check whether this IntervalSet contains only isolated numbers.

        :rtype: bool
        """
        for i in self.ints:
            if not i.is_discrete():
                return False
        return True

    def iter_members(self):
        """
        Iterate over all elements of the set.

        :raises ValueError: if self is a set of everything
        """
        if not self.is_discrete():
            raise ValueError("non-discrete IntervalSet can not be iterated")
        for i in self.ints:
            yield i.get_point()

    def intersection(self,other):
        """
        Return a new IntervalSet with the intersection of the two sets, i.e.
        all elements that are both in self and other.

        :param IntervalSet other: Set to intersect with
        :rtype: IntervalSet
        """
        res = []
        for i1 in self.ints:
            for i2 in other.ints:
                res.append(i1.intersection(i2))

        return IntervalSet(res)

    def union(self,other):
        """
        Return a new IntervalSet with the union of the two sets, i.e.
        all elements that are in self or other.

        :param IntervalSet other: Set to intersect with
        :rtype: IntervalSet
        """
        return IntervalSet(self.ints + other.ints)

    def difference(self,other):
        """
        Return a new IntervalSet with the difference of the two sets, i.e.
        all elements that are in self but not in other.

        :param IntervalSet other: Set to subtract
        :rtype: IntervalSet
        """
        res = IntervalSet.everything()
        for j in other.ints:
            tmp = []
            for i in self.ints:
                tmp.extend(i._difference(j))
            res = res.intersection(IntervalSet(tmp))
        return res

    def __contains__(self,x):
        """
        Check membership of the element.

        :param element: Element to check membership of
        :rtype: bool
        """
        for interval in self.ints:
            if x in interval:
                return True
        return False

    def __str__(self):
        if self.is_empty():
            return "<empty interval set>"
        else:
            return " u ".join(str(i) for i in self.ints)

    def __repr__(self):
        return "IntervalSet([%s])" % ",".join(i.__repr__() for i in self.ints)


class DiscreteSet(object):
    """
    A set data structure for hashable elements

    This is a wrapper around pythons set type, which additionally provides
    the possibility to express the set of everything (which only makes sense
    sometimes).
    """
    def __init__(self,elements):
        """
        Create a new DiscreteSet

        :param sequence elements: The elements of the newly created set
        """
        self.everything = False
        self.elements = frozenset(elements)

    @classmethod
    def everything(cls):
        """
        Create a new set of everything.

        One can not iterate over the elements of this set, but many
        operations are actually well defined and useful.
        """
        res = cls([])
        res.everything = True
        return res

    def is_empty(self):
        """
        Check whether the set is empty

        :rtype: bool
        """
        if self.everything:
            return False
        return len(self.elements) == 0

    def is_discrete(self):
        """
        Check whether the set is discrete, i.e. if :meth:`iter_members` can
        be used.

        :rtype: bool
        """
        return not self.everything

    def intersection(self,other):
        """
        Return a new DiscreteSet with the intersection of the two sets, i.e.
        all elements that are in both self and other.

        :param DiscreteSet other: Set to intersect with
        :rtype: DiscreteSet
        """
        if self.everything:
            if other.everything:
                return DiscreteSet()
            else:
                return DiscreteSet(other.elements)
        else:
            if other.everything:
                return DiscreteSet(self.elements)
            else:
                return DiscreteSet(self.elements.intersection(other.elements))

    def difference(self,other):
        """
        Return a new DiscreteSet with the difference of the two sets, i.e.
        all elements that are in self but not in other.

        :param DiscreteSet other: Set to subtract
        :rtype: DiscreteSet
        :raises ValueError: if self is a set of everything
        """
        if self.everything:
            raise ValueError("Can not remove from everything")
        elif other.everything:
            return DiscreteSet([])
        else:
            return DiscreteSet(self.elements.difference(other.elements))

    def union(self,other):
        """
        Return a new DiscreteSet with the union of the two sets, i.e.
        all elements that are in self or in other.

        :param DiscreteSet other: Set to unite with
        :rtype: DiscreteSet
        """
        if self.everything:
            return self
        elif other.everything:
            return other
        else:
            return DiscreteSet(self.elements.union(other.elements))

    def iter_members(self):
        """
        Iterate over all elements of the set.

        :raises ValueError: if self is a set of everything
        """
        if self.everything:
            raise ValueError("Can not iterate everything")
        for coord in sorted(self.elements):
            yield coord

    def __contains__(self,element):
        """
        Check membership of the element.

        :param element: Element to check membership of
        :rtype: bool
        """
        if self.everything:
            return True
        return element in self.elements

    def __str__(self):
        if self.is_empty():
            return "<empty discrete set>"
        else:
            return "{%s}" % ",".join(str(e) for e in sorted(self.elements))

    def __repr__(self):
        if self.everything:
            return "DiscreteSet.everything()"
        return "DiscreteSet([%s])" % ",".join(i.__repr__() for i in sorted(self.elements))


#These are not used or documented at the moment, but might be useful in the
#future

class Patch(object):
    def __init__(self,sets):
        """
        A patch of multidimensional parameter space

        sets is a dict of names to DiscreteSet or IntervalSets of feasible
        values and represents the cartesion product of these
        """
        self.sets = sets
        self.discrete = True
        self.empty = False
        for s in sets.values():
            if isinstance(s,IntervalSet) and not s.is_discrete():
                self.discrete = False
            if s.is_empty():
                self.empty = True

    def is_empty(self):
        return self.empty

    def is_discrete(self):
        return self.discrete

    def intersection(self,other):
        "intersection with another patch"
        res = {}
        if set(self.sets.keys()) != set(other.sets.keys()):
            raise KeyError('Incompatible patches in intersection')
        for name,s1 in self.sets.items():
            s2 = other.sets[name]
            res[name] = s1.intersection(s2)
        return Patch(res)

    def iter_points(self):
        "returns a list of tuples of names and values"
        if not self.is_discrete():
            raise ValueError("Patch is not discrete")
        names = sorted(self.sets.keys())
        icoords = [self.sets[name].iter_members() for name in names]
        for coordinates in product(*icoords):
            yield tuple(zip(names,coordinates))

    def __contains__(self,point):
        for name, coord in point.items():
            if not coord in self.sets[name]:
                return False
        return True

    def __str__(self):
        if self.is_empty():
            return "<empty patch>"
        else:
            sets = ["%s:%s" % (n,str(i)) for n,i in self.sets.items()]
            return " x ".join(sets)

class PatchSet(object):
    """
    A list of patches that represents quite general subsets of a
    multidimensional parameter space
    """
    def __init__(self,patches):
        self.discrete = True
        self.patches = []
        self.coords = None
        for patch in patches:
            if patch.is_empty():
                continue
            if not patch.is_discrete():
                self.discrete = False
            self.patches.append(patch)

    def is_empty(self):
        return len(self.patches) == 0

    def is_discrete(self):
        return self.discrete

    def intersection(self,other):
        res = []
        for p1 in self.patches:
            for p2 in other.patches:
                res.append(p1.intersection(p2))
        return PatchSet(res)

    def iter_points(self):
        if not self.discrete:
            raise ValueError('cannot iter points in non-discrete domain')
        if self.coords is None:
            self.coords = set([])
            for patch in self.patches:
                for point in patch.iter_points():
                    self.coords.add(point)
        for coord in self.coords:
            yield coord

    def __contains__(self,point):
        for patch in self.patches:
            if point in patch:
                return True
        return False

    def __str__(self):
        if self.is_empty():
            return "<empty interval set>"
        else:
            return "{ %s }" % " u ".join(str(i) for i in self.ints)

