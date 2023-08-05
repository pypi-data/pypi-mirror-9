
def build_ext(*args,**kargs):
    '''
    Wrapper over the build_ext class to postpone the import of cython
    '''
    from build_ext import build_ext as _build_ext
    return _build_ext(*args,**kargs)
