#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
functions of time which evaluate to (position, velocity, acceleration, jerk) tuples
"""

__author__ = "Philippe Guglielmetti"
__copyright__ = "Copyright 2013, Philippe Guglielmetti"
__credits__= ["http://osterone.bobstgroup.com/wiki/index.php?title=UtlCam"]
__license__ = "LGPL"

from .piecewise import *
from .polynomial import Polynomial
from .itertools2 import any
from .math2 import quad, equal

class PVA(object):
    """represents a function of time returning position, velocity, and acceleration
    """
    
    def __init__(self,funcs):
        self.funcs=funcs
        
    def __call__(self,t,t0=0):
        return tuple(f(t-t0) for f in self.funcs)

class Segment(PVA):
    """ a PVA defined between 2 times, null elsewhere
    """
    
    def __init__(self,t0,t1,funcs):
        super(Segment, self).__init__(funcs)
        self.t0=t0
        self.t1=t1
        
    def dt(self):
        return self.t1-self.t0
        
    def start(self):
        return super(Segment, self).__call__(self.t0, self.t0)
    
    def end(self):
        return super(Segment, self).__call__(self.t1, self.t0)
        
    def __call__(self,t):
        if t>=self.t0 and t<self.t1:
            return super(Segment, self).__call__(t, self.t0)
        else:
            return (0,)*len(self.funcs)
    
class SegmentPoly(Segment):
    """ a segment defined by a polynomial position law
    """
    def __init__(self,t0,t1,p):
        p=Polynomial(p)
        v=p.derivative()
        a=v.derivative()
        j=a.derivative()
        super(SegmentPoly, self).__init__(t0,t1,(p,v,a,j))
        
def _pva(val):
    try: p=val[0]
    except: p=val
    try: v=val[1]
    except: v=None
    try: a=val[2]
    except: a=None
    return p,v,a
           
def _delta(x0,x1):
    try:
        return float(x1-x0)
    except:
        return None
    
def ramp(dp,v0,v1,a):
    """
    :param dp: float delta position or None if unknown
    :param v0: float initial velocity or None if unknown
    :param v1: float final velocity or None if unknown
    :param a: float acceleration
    :return: float shortest time to accelerate between constraints
    """
    dt=[]
    dv=_delta(v0,v1)
    if dv:
        dt.append(dv/a) #time to accelerate
    try: # solve a.t^2/2+v0.t == dp
        dt.extend(list(quad(a/2.,v0,-dp)))
    except: 
        try: # solve v1.t-a.t^2/2 == dp
            dt.extend(list(quad(-a/2.,v1, -dp)))
        except: pass
    return min(t for t in dt if t > 0) #return smallest positive

def trapeze(dp,vmax,a,v0=0,v2=0):
    """
    :param dp: float delta position
    :param vmax: float maximal velocity
    :param a: float acceleration
    :param v0: float initial velocity, 0 by default 
    :param v2: float final velocity, 0 by default 
    :return: tuple of 6 values:
    
    * time at end of acceleration
    * position at end of acceleration
    * velocity at end of acceleration
    * time at begin of deceleration
    * position at begin of deceleration
    * total time
    """
    t1=ramp(dp/2.,v0,vmax,a) #acceleration time
    v1=v0+a*t1 #speed reached
    p1=t1*(v0+v1)/2. #position at end of acceleration
    t3=ramp(dp/2.,v1,v2,-a) #deceleration time
    p2=t3*(v1+v2)/2. #distance to decelerate
    t2=float(dp-p1-p2)/v1 #time at constant velocity
    return t1,p1,v1,t1+t2,dp-p2,t1+t2+t3
    
def Segment2ndDegree(t0,t1,start,end=(None)):
    """calculates a constant acceleration Segment between start and end
    
    :param t0,t1: float start,end time. one of both may be None for undefined
    :param start: (position, velocity, acceleration) float tuple. some values may be None for undefined
    :param end: (position, velocity, acceleration) float tuple. some values may be None for undefined
    :return: :class:`SegmentPoly`
    
    the function can cope with almost any combination of defined/undefined parameters,
    among others (see tests):
    
    * Segment2ndDegree(t0,t1,(p0,v0),p1) # time interval and start + end positions  + initial speed
    * Segment2ndDegree(t0,t1,(p0,v0,a)) # time interval and start with acceleration
    * Segment2ndDegree(t0,t1,None,(p1,v1,a)) # time interval and end pva
    * Segment2ndDegree(t0,None,(p0,v0),(p1,v1)) # start + end positions + velocities
    * Segment2ndDegree(t0,None,(p0,v0,a),(None,v1)) # start pva + end velocity
    * Segment2ndDegree(None,t1,p0,(p1,v1,a)) # end pva + start position
    
    the function also accepts some combinations of overconstraining parameters:
    
    * Segment2ndDegree(t0,t1,(p0,v0,a),p1) # time interval, start pva, end position => adjust t1
    * Segment2ndDegree(t0,t1,(p0,v0,a),(None,v1)) # time interval, start pva, v1=max vel => adjust t1
    
    :raise ValueError: when not enough parameters are specified to define the Segment univoquely
    
    """
    p0,v0,a0=_pva(start)
    p1,v1,a1=_pva(end)
    if a0 is None: a0=a1
    #to handle the many possible cases, we evaluate missing information in a loop
    for retries in range(2): #two loops are enough to solve all cases , according to tests   
        dt=_delta(t0,t1)
        dp=_delta(p0,p1)
        dv=_delta(v0,v1)
        
        if not any((dt,p0,v0,a0),lambda x:x is None): #we have all required data
            res=SegmentPoly(t0,t1,[p0,v0,a0/2.])
            end=res.end()
            if p1 is not None and not equal(end[0],p1): #consider p1 as max position
                res2=Segment2ndDegree(t0,None,(p0,v0,a0),p1)
                if res2.dt()<res.dt(): #this case arises earlier
                    res=res2
            if v1 is not None and not equal(end[1],v1): #consider v1 as max velocity
                res2=Segment2ndDegree(t0,None,(p0,v0,a0),(None,v1))
                if res2.dt()<res.dt(): #this case arises earlier
                    res=res2
            return res

        if dt is None: #try to determine it from available params
            if a0:
                dt=ramp(dp,v0,v1,a0)
            else:
                try:
                    dt=2.*dp/(v0+v1) #time to reach the position
                except: pass

        if t0 is None:
            try: t0=t1-dt
            except: pass
        if t1 is None: 
            try: t1=t0+dt
            except: pass
                
        if a0 is None:
            try: a0=float(dv)/dt
            except:
                try: a0=2.*(dp-v0*dt)/dt*dt
                except: pass
        if v0 is None:
            try: v0=v1-a0*dt
            except: pass
        if p0 is None:
            try: p0=p1-dt*float(v1+v0)/2.
            except: pass
    
    raise ValueError
    
def Segment4thDegree(t0,t1,start,end):
    """smooth trajectory from an initial position and initial speed (p0,v0) to a final position and speed (p1,v1)
    * if t1<=t0, t1 is calculated
    """
    p0,v0,a0=_pva(start)
    p1,v1,a1=_pva(end)
    
    if t1<=t0:
        dt=float(p1-p0)/((v1-v0)/2. + v0) #truediv
        t1=t0+dt
    else:
        dt=t1-t0
    return SegmentPoly(t0,t1,[p0,v0,0,float(v1-v0)/(dt*dt),-float(v1-v0)/(2*dt*dt*dt)]) #truediv


def SegmentTrapezoidalSpeed(t0,p0,p1,a,T=0,vmax=float('inf')):
    """
    :param t0: float start time
    :param p0: float start position
    :param p1: float end position
    :param a: float specified acceleration. if =0, use specified time
    :param T: float specified time. if =0 (default), use specified acceleration
    :param vmax: float max speed. default is infinity (i.e. triangular speed)
    """
    return