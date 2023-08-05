def isprime(x):
    count = 0;i=1
    if((x%2==0 and x!=2) or (x%3==0 and x!=3) or (x%5==0 and x!=5) or (x%7==0 and x!=7) or (x<2)):
        return False
    else:
        while(i<=(x/2)):
            if(x%i==0):
                count+=1
            i+=1
    if(count>1):
       return False
    else:
       return True

def all_PrimeNumbers_within(y):
    i=2; j=[]
    while(i<y):
        if(isprime(i)):
            j.append(i)
        i+=1
    return j

def all_PrimeNumbers_inRange(x,y):
    i=x; j=[]
    while(i<y):
        if(isprime(i)):
            j.append(i)
        i+=1
    return j

        
