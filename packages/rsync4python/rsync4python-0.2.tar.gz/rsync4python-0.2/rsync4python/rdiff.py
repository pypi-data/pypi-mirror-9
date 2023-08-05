import sys

import rsync4python.rsync


def rdiff_signature(basefilename, signature_filename):

    with open(basefilename, 'rb') as base:
        with open(signature_filename, 'wb') as signature:
            rsync4python.rsync.rsync.signature(base, signature)


def rdiff_patch(basefilename, deltafilename, finalfilename):

    with open(basefilename, 'rb') as base:
        with open(deltafilename, 'rb') as delta:
            with open(finalfilename, 'wb') as final:
                rsync4python.rsync.rsync.patch(base, delta, final)
