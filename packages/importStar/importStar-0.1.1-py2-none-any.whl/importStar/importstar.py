'''
Created on 3 Sep 2014

@author: elkb4
'''

__help__ = """
usage: importStar [package-path]

modifies the following lines in each __init__.py file:
==============

#<<<importStar
[i get modified]
#>>>importStar

TO
=============
#<<<importStar
import module1
import mopduleN
import package1
import packageN
#>>>importStar

"""

import os

def run(argv):
    if not argv[1:] or argv[1] in ('-h', '--help'):
        sys.exit(__help__)
    path = argv[1]
    if not os.path.exists(path):
        sys.exit("ERROR: given path '%s' not valid" %path)
    inits = findInit(path)
    print 'found %s __init__.py files' %len(inits)
    for path in inits:
        start, stop, lines = findRange(path)
        if stop != None:
            modules = getModulesInDir(os.path.dirname(path))
            if modules:
                modifyInit(path, lines, modules, start, stop)
    print 'done.'



def findInit(path):
    inits = []
    def recursive(path):
        for f in os.listdir(path):
            p = os.path.join(path,f)
            if os.path.isdir(p):
                recursive(p)
            elif f == '__init__.py':
                inits.append(p)
    recursive(path)
    return inits


def findRange(initpath):
    start = None
    stop = None
    with open(initpath, 'r') as init:
        lines = init.readlines()
        for n,line in enumerate(lines):
            if '#<<<importStar' in line:
                start = n+1 #start after #<<...
            elif start != None and '#>>>importStar' in line:
                stop = n
                break
    return start, stop, lines


def getModulesInDir(path):
    l = []
    for x in os.listdir(path):
    # do not import ... __init__.py files
        if (x != '__init__.py' 
                #... pyc-files
                and not x.endswith('pyc') 
                #... files that that with a number (would give import error)
                and not x[0].isdigit()):
            d = os.path.join(path,x) 
            if os.path.isdir(d):
                if not os.path.exists(
                    os.path.join(d,'__init__.py')):
                    #...folders without __init__.py files 
                    continue
            elif not x.endswith('py'):
                # ... non py-files
                continue
            l.append(x.split('.')[0])
    return l         
    #return [x.split('.')[0] for x in os.listdir(path) if x != '__init__.py' and not x.endswith('pyc')]


def modifyInit(initpath, lines, modules, start, stop):
    importLines = ['import %s\n' %x for x in modules]
    newLines = list(lines[:start])
    newLines.extend(importLines)
    newLines.extend(lines[stop:])
    with open(initpath, 'w') as init:
        init.writelines(newLines)
    
if __name__ == '__main__':
    import sys
    run(sys.argv)

# print 66'
                
