def f(z):
    A=[]
    B=[]
    C=[]
    for i in range(1,27):
        A.append(i)
    for i in range(65,91):
        x=chr(i)
        B.append(x)
    a=dict(zip(A,B))
    for i in z:
        y=dict.keys(ord(i))
        C.append(y)
    return C

n=str(input())
print(f(n))
