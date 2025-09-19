import numpy as np
import math
from location import locator

#DO NOT QUESTION
def L(x_1, x_2, y_1, y_2, R_1, R_2, d):
    return 2 * d**2 * math.log(R_2/R_1) + y_2 ** 2 - y_1 ** 2 - x_1 **2 + x_2 **2

def K(x_1, x_3, y_1, y_3, R_1, R_3, d):
    return x_1 ** 2 - x_3 ** 2 - y_3 ** 2 + y_1 ** 2 - 2 * d ** 2 * math.log(R_3 / R_1)

def M(y_1, y_3):
    return (1 / (2 * (y_1 - y_3)))

def x_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d):
    l = L(x_1, x_2, y_1, y_2, R_1, R_2, d)
    k = K(x_1, x_3, y_1, y_3, R_1, R_3, d)
    m = M(y_1, y_3)

    return (l - 2 * y_2 * m * k + 2 * y_1 * m * k)/(-2 * x_1 + 2 * x_2 - 4 * x_1 * y_2 * m + 4 * x_3 * y_2 * m+ 4 * x_1 * y_1 * m - 4 * y_1 * x_3 * m)

def y_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d):
    x = x_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d)
    k = K(x_1, x_3, y_1, y_3, R_1, R_3, d)


    return (k - 2 * x_1 * x + 2 * x_3 * x) / (2 * (y_1 - y_3))






def R(m,x, y, x_0, y_0, d):
    return m * math.exp(-((x-x_0)**2 + (y-y_0)**2)/(2*d**2))

#Test
# e = math.e
# p = math.pi
# x_1, y_1 = -10 * e, p
# x_2, y_2 = e ** p, p ** e
# x_3, y_3 = 6 * e/p, -p/e

# origin = 6, 6
# d = 20
# max = 1 / (2 * math.pi * d**2)

# R_1 = R(max,x_1, y_1, origin[0], origin[1], d)
# R_2 = R(max,x_2, y_2, origin[0], origin[1], d)
# R_3 = R(max,x_3, y_3, origin[0], origin[1], d)




# center_x, center_y = x_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d), y_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d)

# print(center_x,center_y)

csv = [
    "point1.csv",
    "point2.csv",
    "point3.csv"
]

point = locator(csv)

point.readcsv()

point.getRate()

e = math.e
p = math.pi
x_1, y_1 = -10 * e, p
x_2, y_2 = e ** p, p ** e
x_3, y_3 = 6 * e/p, -p/e

R_1, R_2, R_3 = point.rates 

d = 20

center_x, center_y = x_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d), y_0(x_1, x_2, x_3, y_1, y_2, y_3, R_1, R_2, R_3, d)

print(center_x,center_y)