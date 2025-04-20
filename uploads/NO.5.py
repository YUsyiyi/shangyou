import random
a=["001","002","003","100"]
for i in range(5):
    c=int(random.randint(0,4))
    print("6101009"+a[c],end=" ")
    for j in range(3):
        b=random.randint(97,122)
        print(chr(b),end="")
        d=random.randint(0,9)
        print(d,end="")
    print("\n")



