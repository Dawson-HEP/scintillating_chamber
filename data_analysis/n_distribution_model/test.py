def num_of_1(n):
    return str(bin(n)).count("1")

# print(num_of_1(263430))


k = 1
for i in range(722):
    k = (k * 3 ) % 11

print(k)
    

k = 1
for i in range(541):
    k = (k * 3 ) % 11

print(k)