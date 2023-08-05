from itertools import chain

def fisher_hyper (a,b,c,d):
    p=1.0
    #j=a+b+c+d
    #i=d
    div = chain(range(a+b+1, a+b+c+d+1), range(2, d+1))
    try:
        for x,y in ((a,c), (c,d), (b,d)):
            for f in range(x+1,x+y+1):
                # print(p)
                p = p*f
                if p > 1:
                    for n in div:
                        p = p/n
                        if p < 1:
                            break
        for n in div:
            p = p/n
    except ZeroDivisionError:
        print('uups')
        p = 0.
    #print(p)
    return p


def fisher (a,b,c,d, sided=0):
    """sided =0 means right-sided test - the only one implemented here."""

    p = fisher_hyper(a,b,c,d)
    r = p
    while b and c:
        a+=1
        d+=1
        r=r*b*c/(a*d)
        p+=r
        b-=1
        c-=1
    return p
