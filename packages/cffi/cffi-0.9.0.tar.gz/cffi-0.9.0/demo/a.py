import cffi
ffi = cffi.FFI()
ffi.cdef('int foo();')
lib = ffi.verify('int foo();', sources=['a.cpp'], force_generic_engine=True)
print(lib.foo())
