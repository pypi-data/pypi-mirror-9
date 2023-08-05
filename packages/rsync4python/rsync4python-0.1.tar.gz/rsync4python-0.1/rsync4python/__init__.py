"""
rsync4python
"""

import rsync4python.rsync as rsync

signature = rsync.rsync.signature
patch = rsync.rsync.patch

RS_DONE = 0  # Completed successfully
RS_BLOCKED = 1  # Blocked waiting for more data
RS_RUNNING = 2  # Not yet finished or blocked; this value should never be returned to caller
RS_TEST_SKIPPED = 77  # Test neither passed or failed
RS_IO_ERROR = 100  # Error in file or network IO
RS_SYNTAX_ERROR = 101  # command-line syntax error
RS_MEM_ERROR = 102  # out of memory
RS_INPUT_ENDED = 103  # end of input file, possibly unexpected
RS_BAD_MAGIC = 104  # bad magic number at start of stream
                    # probably not a librsync file or possibly the
                    # wrong kind of file or from an incompatible library version
RS_UNIMPLEMENTED = 105  # librsync author was lazy
RS_CORRUPT = 106  # unbelievable value in stream
RS_INTERNAL_ERROR = 107  # probably a librsync library bug
RS_PARAM_ERROR = 108  # bad value passed in to libray
                      # probably an application bug
