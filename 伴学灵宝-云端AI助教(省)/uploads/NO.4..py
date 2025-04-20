def age(x):
    if x==1:
        return 10
    else:
        return age(x-1)+2

print(age(5))