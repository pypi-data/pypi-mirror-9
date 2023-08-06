import cffi

ffi = cffi.FFI()


ffi.cdef("""
struct foo_s {
    int a, b, c;
    ...;
};
""")

lib = ffi.verify("""
struct foo_s {
    int b, d, a;
    const int c;
};
""")

s = ffi.new("struct foo_s *")
for name in ('a', 'b', 'c'):
    print ffi.offsetof("struct foo_s", name)
