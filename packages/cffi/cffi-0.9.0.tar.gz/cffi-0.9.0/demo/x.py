from cffi import FFI
ffi = FFI()
ffi.cdef("void myprint();")
C = ffi.verify("""
#include "test.c"
""", include_dirs=['.'])
C.myprint()
