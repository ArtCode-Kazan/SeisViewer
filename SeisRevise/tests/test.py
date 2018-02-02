import numpy as np

s=np.array([0,1,2,3,4])
a=np.array([[0,1],[1,2],[2,3],[3,4],[4,5]])

a1=1<s
b1=s<5
c=a1 * b1
print(a1)
print(b1)
print(c)
print(a[(1<s)*(s<5)])



