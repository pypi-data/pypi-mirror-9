#!env python
#
import os,sys

def generate_caError():
    os.system("rm /caErrorGenerator")
    os.system("gcc -I/Users/Shared/SRC/EPICS/R314/base/include gen_caerrpy.c -o caErrorGenerator")
    os.system("./caErrorGenerator >caError.py")


if __name__ == "__main__":
    generate_caError()
