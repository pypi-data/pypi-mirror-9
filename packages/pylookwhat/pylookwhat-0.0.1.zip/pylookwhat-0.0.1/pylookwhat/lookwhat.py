
import re
from copy import deepcopy
import ast

def lookwhat( filename, res, nameList ):
    pt = re.compile( r'\s*(\w+)\s*=([^=\n]*)' )
    ptcomm = re.compile( '#[^\n]*' )
    _branchs=[
        ['{','}', 0 ],
        ['"','"', 0 ],
        ['[',']', 0 ],
        ['\'','\'', 0 ]
    ]

    usebranch = deepcopy( _branchs )

    rslt = res
    pstep = 0
    psname = ''
    templines = []
    try:
        f = open( filename, 'r' )
        fc = f.readlines()
        for line in fc:
            line = ptcomm.sub( '', line )  # remove comment
            if pstep == 0:
                m = pt.match( line )
                if m:
                    name = m.groups()[0]
                    if name in nameList:
                        pstep = 1
                        psname = name    
                        line = line[ line.find('=')+1 : ]
                        usebranch = deepcopy( _branchs )
            if pstep == 1:
                for c in line:
                    for b in usebranch:
                        if c == b[0]:
                            b[2] += 1
                        if c == b[1]:
                            b[2] -= 1
                nb = False
                for b in usebranch:
                    if b[2] !=0:
                        nb = True
                        break
                templines.append( line )#.strip() # remove newline
                if not nb:
                    pstep = 2

            if pstep == 2:
                #dtext = templines 
                dtext = psname + '='+ "".join(templines)
                #print( dtext )
                g = {} 
                l = {}
                #u = eval( dtext, g, l )
                #g = ast.literal_eval( dtext )
                exec( dtext, g, l )
                fvar = rslt.get( psname )
                g = l.get(psname)
                if fvar:
                    fvar.update( g )
                else:
                    rslt[psname] = g
                    
                pstep = 0
                templines = []
                psname = ''
                


    finally:
        if f:
            f.close()
    return rslt

# Other two ways to get values
# 1. use single line parse with ast.literal_eval
# 2. use exec and get from local variables


if __name__=='__main__':
    what = {}
    lookwhat( 'test.source', myvars, ['DATABASES', 'DEBUG'] )

    print what