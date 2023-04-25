import copy


a="hola/perro/fdf/"
n=0
f=0
lista=[]
for x in range(len(a)):
    if a[x]=="/":
        lista.append(x)

    t=False
    if x=="/" and not t:
        n=n+1
        if n==1:
            ind1=copy.deepcopy(a.index(x))
b=copy.deepcopy(a)
for s in b:
    if s=="/":
        f=f+1
        if f==3:
            ind2=b.index(s)


c=a[lista[0]+1:lista[1]]

print(c)
