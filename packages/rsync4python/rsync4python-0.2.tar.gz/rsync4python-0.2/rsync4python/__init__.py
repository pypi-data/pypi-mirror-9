"""
rsync4python
"""
import rsync4python.rsync as rsync

signature = rsync.rsync.signature
patch = rsync.rsync.patch

# Completed successfully
RS_DONE = 0

# blocked waiting for more data
RS_BLOCKED = 1

# not yet finished or blocked;
# this value should never be returned to caller
RS_RUNNING = 2

# test neither passed nor failed
RS_TEST_SKIPPED = 77

# error in file or etwork i/o
RS_IO_ERROR = 100

# command-line syntax error
RS_SYNTAX_ERROR = 101

# out of memory
RS_MEM_ERROR = 102

# end of input file, possibly unexpected
RS_INPUT_ENDED = 103

# bad magic number at start of stream
# probably not a librsync file or possibley the wrong
# kind of files or from an incompatible library version
RS_BAD_MAGIC = 104

# librsync author was lazy
RS_UNIMPLEMENTED = 105

# unbelievable value in stream
RS_CORRUPT = 106

# probably a librsync library bug
RS_INTERNAL_ERROR = 107

# bad value passed into library, probably an application bug
RS_PARAM_ERROR = 108
