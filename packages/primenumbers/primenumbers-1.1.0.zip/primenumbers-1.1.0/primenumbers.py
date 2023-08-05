def isprime(x):
    count = 0;i=1
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

        
