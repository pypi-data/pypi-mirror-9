from __future__ import print_function,division
import logging

try:
    import numpy as np
except ImportError:
    np = None

from ..hashutils import hasharray, hashcombine, hashdict

class Constraint(object):
    """
    Base class for all constraints to be applied to StarPopulations.
    """
    def __init__(self,mask,name='',**kwargs):
        self.name = name
        self.ok = mask
        self.wok = np.where(self.ok)[0]
        self.frac = float(self.ok.sum())/np.size(mask)
        for kw in kwargs:
            setattr(self,kw,kwargs[kw])

    def __eq__(self,other):
        return hash(self) == hash(other)

    def __ne__(self,other):
        return not self.__eq__(other)

    def __hash__(self):
        return hashcombine(hash(self.name), hasharray(self.ok))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s: %s>' % (type(self),str(self))

class ConstraintDict(dict):
    """
    A dictionary that is hashable.
    """
    def __hash__(self):
        return hashdict(self)

class JointConstraintAnd(Constraint):
    def __init__(self,c1,c2,name='',**kwargs):
        self.name = name
        mask = ~(~c1.ok & ~c2.ok)
        Constraint.__init__(self,mask,name=name,**kwargs)

class JointConstraintOr(Constraint):
    def __init__(self,c1,c2,name='',**kwargs):
        self.name = name
        mask = ~(~c1.ok | ~c2.ok)
        Constraint.__init__(self,mask,name=name,**kwargs)

class RangeConstraint(Constraint):
    def __init__(self,vals,lo,hi,name='',**kwargs):
        self.lo = lo
        self.hi = hi
        Constraint.__init__(self,(vals > lo) & (vals < hi),
                            name=name,vals=vals,lo=lo,hi=hi,**kwargs)

    def __str__(self): #implement default string formatting better.....TODO
        return '{} < {} < {}'.format(self.lo,self.name,self.hi)

class UpperLimit(RangeConstraint):
    def __init__(self,vals,hi,name='',**kwargs):
        RangeConstraint.__init__(self,vals,name=name,lo=-np.inf,hi=hi,**kwargs)
        
    def __str__(self):
        return '{} < {}'.format(self.name,self.hi)    

class LowerLimit(RangeConstraint):
    def __init__(self,vals,lo,name='',**kwargs):
        RangeConstraint.__init__(self,vals,name=name,lo=lo,hi=np.inf,**kwargs)

    def __str__(self):
        return '{} > {}'.format(self.name,self.lo)

class MeasurementConstraint(RangeConstraint):
    def __init__(self,vals,val,dval,thresh=3,name='',**kwargs):
        lo = val - thresh*dval
        hi = val + thresh*dval
        RangeConstraint.__init__(self,vals,lo,hi,name=name,val=val,
                                 dval=dval,thresh=thresh,**kwargs)

class FunctionLowerLimit(Constraint):
    def __init__(self,xs,ys,fn,name='',**kwargs):
        Constraint.__init__(self,ys > fn(xs),name=name,xs=xs,ys=ys,fn=fn,**kwargs)
    
class FunctionUpperLimit(Constraint):
    def __init__(self,xs,ys,fn,name='',**kwargs):
        Constraint.__init__(self,ys < fn(xs),name=name,
                            xs=xs,ys=ys,fn=fn,**kwargs)
    
