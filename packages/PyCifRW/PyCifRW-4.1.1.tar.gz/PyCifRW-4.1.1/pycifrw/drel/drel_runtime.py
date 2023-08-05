import numpy
def aug_append(current,extra):
    """Add the contents of extra to current"""
    have_list = isinstance(current,list)
    if have_list:
        if isinstance(extra, (float,int,complex)):
            #append a single element
            return current + [extra]
        elif isinstance(extra,list):
            return current + extra
    else:
        raise ValueError, "Cannot append %s to %s" % (`extra`,`current`)

def aug_add(current,extra):
    """Sum the contents of extra to current"""
    have_list = isinstance(current,list)
    if have_list:
        if isinstance(extra, (float,int)):
           # requires numpy 
           return numpy.array(current) + extra
        elif isinstance(extra, list):
           return numpy.array(current) + numpy.array(extra)
    else:
        return current + extra

def aug_sub(current,extra):
   have_list = isinstance(current,(list,numpy.ndarray))
   if have_list:
        if isinstance(extra, (float,int)):
           # requires numpy 
           return numpy.array(current) - extra
        elif isinstance(extra, (list,numpy.ndarray)):
           return numpy.array(current) - numpy.array(extra)
   else:
        return current - extra

def aug_remove(current,extra):
    """Remove extra from current. Not in formal
       specifications"""
    have_list = isinstance(current,list)
    if have_list:
        if extra in current:
            # not efficient as we modify in place here
            current.remove(extra)
            return current
    else:
        raise ValueError, "Cannot remove %s from %s" % (`extra`,`current`)

def drel_dot(first_arg,second_arg):
    """Perform a multiplication on two unknown types"""
    print "Multiply %s and %s" % (`first_arg`,`second_arg`)
    def make_numpy(input_arg):
        if hasattr(input_arg,'__iter__'):
            try:
                return numpy.matrix(input_arg),True
            except ValueError:
                raise ValueError, 'Attempt to multiply non-matrix object %s' % (`input_arg`)
        return input_arg,False
    fa,first_matrix = make_numpy(first_arg)
    sa,second_matrix = make_numpy(second_arg)
    if first_matrix and second_matrix:  #mult of 2 non-scalars
        if sa.shape[0] == 1:  #is a row vector
           as_column = sa.T
           result = (fa * as_column).T
        else:
           result = fa * sa
       # detect scalars
        if result.size == 1:
            return result.item(0)
        else: return result   #leave column/row vectors alone for now
    return fa * sa

def drel_add(first_arg,second_arg):
    """Separate string addition from the rest"""
    if isinstance(first_arg,basestring) and isinstance(second_arg,basestring):
        return first_arg+second_arg
    else:
        return numpy.add(first_arg,second_arg)

