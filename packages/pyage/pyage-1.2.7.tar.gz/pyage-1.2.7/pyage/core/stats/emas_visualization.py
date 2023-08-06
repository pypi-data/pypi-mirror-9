# Create the data.
from numpy import pi, sin, cos, mgrid

dphi, dtheta = pi / 20.0, pi / 10.0
[phi, theta] = mgrid[0:2 * pi + dphi * 1.5:dphi, 0:2 * pi + dtheta * 1.5:dtheta]
r = 1
R = 3

x = (R + r * cos(theta)) * cos(phi)
y = (R + r * cos(theta)) * sin(phi)
z = r * sin(theta)

# View it.
from mayavi import mlab

s = mlab.mesh(x, y, z, representation='points', color=(0, 0, 0), scale_factor=0.9, mask=[])
# s = mlab.points3d(x, y, z, color=(0, 0, 0), scale_factor=0.1)
mlab.show()