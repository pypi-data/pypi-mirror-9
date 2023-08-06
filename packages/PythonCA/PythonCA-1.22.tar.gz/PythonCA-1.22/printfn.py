#/bin/env python
#-*- coding:utf-8 -*-
"""
define a printfn function compatible with 
"""
def printfn(*value, **env):
    import sys
    sep=env.get("sep"," ")
    end=env.get('end',"\n")
    file=env.get("file",sys.stdout)
    file.write(sep.join(map(str,value))+end)
