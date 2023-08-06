import cffi

ffi = cffi.FFI()
ffi.cdef('''struct my_struct {
   int a;
   struct {
      int b;
      int c;
   } s;
};''')


def offsetof(type_str, field_names):
    type_ = ffi.typeof(type_str)
    res = 0
    for field_name in field_names.split('.'):
        field = dict(type_.fields)[field_name]
        res += field.offset
        type_ = field.type
    return res


print offsetof('struct my_struct', 's.b')
