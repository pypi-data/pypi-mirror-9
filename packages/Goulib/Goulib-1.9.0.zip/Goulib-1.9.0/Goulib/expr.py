#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
simple symbolic math expressions
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__license__ = "LGPL"

import six, operator, logging, matplotlib

from . import plot #sets matplotlib backend
import matplotlib.pyplot as plt # after import .plot

from . import itertools2

class Expr(plot.Plot):
    """
    Math expressions that can be evaluated like standard functions and combined using standard operators
    """
    def __init__(self,f,left=None,right=None,name=None):
        """
        :param f: function or operator, or Expr to copy construct
        :param left: Expr function parameter or left operand
        :param right: Expr function parameter or left operand
        :param name: string used in repr, preferably in LaTeX
        """
        if isinstance(f,Expr): #copy constructor
            name=f.name
            self.isconstant=f.isconstant
            self.left=f.left
            self.right=f.right
            f=f.y #to construct this object, we take only the function of the source
        if left: # f is an operator
            if not name:
                name=f.__name__
            self.left=Expr(left)
            self.right=Expr(right) if right else None
            self.isconstant=self.left.isconstant and (not self.right or self.right.isconstant)
            if self.isconstant: #simplify
                f=f(self.left.y,self.right.y) if self.right else f(self.left.y)
        else:              
            self.left=None
            self.right=None
            try: #is f a function ?
                f(1)
                self.isconstant=False
                if not name:
                    name='\\%s(x)'%f.__name__ #try to build LateX name
                elif name.isalpha() and name!='x':
                    name='\\'+name
            except: #f is a constant 
                self.isconstant=True
                name=str(f)
        self.name=name
        self.y=f
        
    def __call__(self,x): 
        """evaluate the Expr at x OR compose self(x())"""
        if isinstance(x,Expr): #composition
            return self.applx(x)
        try: #is x iterable ?
            return [self(x) for x in x]
        except: pass
        if self.isconstant:
            return self.y  
        elif self.right:
            l=self.left(x)
            r=self.right(x)
            return self.y(l,r)
        if self.left:
            return self.y(self.left(x))
        else:
            return self.y(x)
        
    def __repr__(self):
        if self.isconstant:
            res=repr(self.y)
        elif self.right: #dyadic operator
            res='%s(%s,%s)'%(self.name,self.left,self.right) # no precedence worries
        elif self.left:
            res='%s(%s)'%(self.name,self.left)
        else:
            res=self.name
        return res.replace('\\','') #remove latex prefix if any
    
    def _repr_latex_(self):
        """:return: LaTex string for IPython Notebook"""
        if self.isconstant:
            res=repr(self.y)
        else:
            name=self.name
            left=''
            if self.left:
                left=self.left._repr_latex_()
                if self.left.left: #complex
                    left='{'+left+'}'
            right=''
            if self.right:
                right=self.right._repr_latex_()
                if self.right.left: #complex
                    right='{'+right+'}'
            if right: #dyadic operator
                res=left+name+right
            elif left: #monadic or function
                if len(name)>1:
                    res='%s(%s)'%(name,left)
                else:
                    res=name+left
            else:
                res=name
        return res
    
    def plot(self, fmt='svg', x=None):
        from IPython.core.pylabtools import print_figure
        import matplotlib.pyplot as plt
        # plt.rc('text', usetex=True)
        fig, ax = plt.subplots()
        if x is None:
            x=itertools2.arange(-1,1,.1)
        x=list(x)
        y=self(x)
        ax.plot(x,y)
        ax.set_title(self._repr_latex_())
        data = print_figure(fig, fmt)
        plt.close(fig)
        return data
    
    def _repr_png_(self):
        return self.plot(fmt='png')

    def _repr_svg_(self):
        return self.plot(fmt='svg')

    def apply(self,f,right=None,name=None):
        """function composition self o f = f(self(x)) or f(self,right)"""
        return Expr(f,self,right, name=name)
    
    def applx(self,f,name=None):
        """function composition f o self = self(f(x))"""
        res=Expr(self) #copy
        res.name=res.name.replace('(x)','')
        res.left=Expr(f,res.left,name=name)
        if res.right:
            res.right=Expr(f,res.right,name=name)
        return res
    
    def __eq__(self,other):
        if self.isconstant:
            try:
                if other.isconstant:
                    return self.y==other.y
            except:
                return self.y==other
        raise NotImplementedError #TODO : implement for general expressions...
    
    def __lt__(self,other):
        if self.isconstant:
            try:
                if other.isconstant:
                    return self.y<other.y
            except:
                return self.y<other
        raise NotImplementedError #TODO : implement for general expressions...

    def __add__(self,right):
        return self.apply(operator.add,right,'+')
    
    def __sub__(self,right):
        return self.apply(operator.sub,right,'-')
    
    def __neg__(self):
        return self.apply(operator.neg,None,'-')
    
    def __mul__(self,right):
        return self.apply(operator.mul,right,'*')
    
    def __rmul__(self,right):
        return Expr(right).apply(operator.mul,self,'*')
    
    def __truediv__(self,right):
        return self.apply(operator.truediv,right,'/')
    
    __div__=__truediv__
    
    def __invert__(self):
        return self.apply(operator.not_,None,'~')
    
    def __and__(self,right):
        return self.apply(operator.and_,right,'&')
    
    def __or__(self,right):
        return self.apply(operator.or_,right,'|')
    
    def __xor__(self,right):
        return self.apply(operator.xor,right,'^')
    
    def __lshift__(self,dx):
        return self.applx(lambda x:x+dx,name='lshift')
    
    def __rshift__(self,dx):
        return self.applx(lambda x:x-dx,name='rshift')

