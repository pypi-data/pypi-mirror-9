def prim(inp):             #get primary number or not
    res=[]
    comp=[]
    for divid in range(1,inp+2):
        if(inp%divid==0):
            res.append(divid)
    if(res==comp):
        return 0          #if it is a primary number
    else:
        return res        #if it isn't a primary number, returns the list of aliquot
def lccd(one,two,mod=0):     #two number and mode.
    if mod==0:        #least common multiple mode.
        e=2
        d=1
        while 1:
            if (one%e==0) and (two%e==0):
                one=one/e
                two=two/e
                d=d*e
            else:
                if e>min(one,two):
                    break
                else:
                    e=e+1
        return d      #returns the least common multiple.
    elif mod==1:    #greatest common measure mode.
        e=2
        d=1
        while 1:
            if (one%e==0) and (two%e==0):
                one=one/e
                two=two/e
                d=d*e
            else:
                if e>min(one,two):
                    d=int(d*one*two)
                    break
                else:
                    e=e+1
        return d        #returns the greatest common measure.

