# A Linux-only demo, using verify() instead of hard-coding the exact layouts
#
import sys
from cffi import FFI

if not sys.platform.startswith('linux'):
    raise Exception("Linux-only demo")


ffi = FFI()
ffi.cdef("""

    typedef ... DIR;

    struct dirent {
        unsigned char  d_type;      /* type of file; not supported
                                       by all file system types */
        char           d_name[...]; /* filename */
        ...;
    };

    int readdir_r(DIR *dirp, struct dirent *entry, struct dirent **result);
    int openat(int dirfd, const char *pathname, int flags);
    DIR *fdopendir(int fd);
    int closedir(DIR *dirp);

    static const int DT_DIR;

""")
ffi.verify("""
#ifndef _ATFILE_SOURCE
#  define _ATFILE_SOURCE
#endif
#ifndef _BSD_SOURCE
#  define _BSD_SOURCE
#endif
#include <fcntl.h>
#include <sys/types.h>
#include <dirent.h>
""", modulename='_readdir3', tmpdir='.')
