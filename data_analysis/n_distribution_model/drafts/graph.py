import numpy as np
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull

#Scale up the matrix so that the data is more percise
scale = 10  #increased by

#Maximum angle of rotation for each axis

max_yaw_deg = 90 * 2       
max_pitch_deg = 13 * 2

max_yaw_rad = np.deg2rad(max_yaw_deg)      
max_pitch_rad = np.deg2rad(max_pitch_deg)  



#Diameter of rotational motion
d_pitch = 125 * 2  #mm
d_yaw = 80 * 2   #mm


#Measurements of rod
l = 10      # mm, facing x
w = 10      # mm, facing y
h = 30      #mm, facing z

#Calculate the matrix size
# i = d_yaw * scale
# j = round((d_pitch * np.sin(max_pitch_rad)) * scale)  #Since this is not 180˚, we must calculate the cross-sectional area

i = 200
j = 200

#Create a template matrix
matrix = np.zeros((i, j))


# for rate in rates:    
## mm
x0 = 0
x1 = 0
y0 = 1
y1 = 1
z0 = 7
z1 = 40

k = 1
# coords = np.array([
#     [x0, y0, z0, k],
#     [x1, y0, z0, k],
#     [x0, y1, z0, k],
#     [x1, y1, z0, k],
#     [x0, y0, z1, k],
#     [x1, y0, z1, k],
#     [x0, y1, z1, k],
#     [x1, y1, z1, k]
# ])

coords = np.array([
    [0.000,  0.000,  0.000,k],
    [1.366,  0.341, -0.434,k],
    [0.683,  0.939, -0.116,k],
    [2.049,  1.280, -0.650,k],
    [0.000,  0.500,  2.598,k],
    [1.366,  0.841,  2.164,k],
    [0.683,  1.439,  2.482,k],
    [2.049,  1.780,  2.048,k]
])

projection_matrix = np.array([
    [0, 1,  0,  0],
    [0, 0,  1,  0],
    [0, 0,  0,  1]
])

coords = (coords + 1) * 10
#Project the matrix onto yz plane
hexagon = np.round((coords @ projection_matrix.T)[:,:2])
#Calculate the convex hull, which is the minimum coordinates that are needed to contain all the points 
hull = ConvexHull(hexagon) 
#Only keep the points that are not duplicated
print(hexagon)

hexagon = hexagon[hull.vertices]

print(hexagon)

#Generate template matrix
matrix = np.zeros((i, j), dtype = int)


#Create a Path Object
hex_path = Path(hexagon)

#Generate all the possible coordinates in the grid
xv, yv = np.meshgrid(np.arange(i), np.arange(j))
points = np.vstack((xv.flatten(), yv.flatten())).T

#Loop through each coordinate and find which points are contained within the hexagon
mask = hex_path.contains_points(points).reshape(i, j)

#Turn the True/False into 1s and 0s
# mask = mask.astype(int) * rate
mask = mask.astype(int) 

matrix += mask


x = np.arange(matrix.shape[1])
y = np.arange(matrix.shape[0])
X, Y = np.meshgrid(x, y)

# Plot

# fig, ax = plt.subplots(subplot_kw={'projection':'3d'})

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, matrix, cmap='terrain')  # 'terrain' colormap looks like mountains
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Frequency")
plt.show()