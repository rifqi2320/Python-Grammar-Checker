N = int(input("Masukan Nilai N: "))
list = [0 for i in range(N)]

for i in range(N):
    list[i] = int(input())

print("Hasil setelah dibalik: ")
for i in range(N-1, -1, -1):
    print(list[i])