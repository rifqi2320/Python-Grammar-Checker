def fungsi(x):
    return x**2 - 2*x + 5 

A = int(input("Masukkan A: "))   B = int(input("Masukkan B: "))

for i in range(A,B+1) : 
    print("f(" + str(i) + ") =", fungsi(i))

