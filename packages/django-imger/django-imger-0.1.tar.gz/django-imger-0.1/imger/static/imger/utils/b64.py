#!/usr/bin/env python
import sys
import os
import base64

if(__name__ == '__main__'):
    arglen = len(sys.argv)
    if arglen > 1:
        imgfile = open(sys.argv[1], 'rb').read()

        with open(sys.argv[1], "rb") as imageFile:
            payload = base64.b64encode(imageFile.read())

        file_name = os.path.splitext(sys.argv[1])
        fname = file_name[0]
        fext = file_name[1]

        b64imgfile = open(fname + fext + '.txt', 'w')
        for line in payload:
            b64imgfile.write(line)
        print fname
        print fext
        print('done')
    else:
        print('No img file specified!')
