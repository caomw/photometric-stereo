# python setup.py build_ext --inplace
import cv2
from mve.core import Scene
s = Scene()
s.load('../tmp/b-daman/scene')
#s.load(0)

views = s.views
print(views)

for v in views:
    print(v.name)

v = views[0]
cam = v.camera
print(cam.position)
print(cam.translation)
print(cam.view_dir)
print(cam.world_to_cam_matrix)
print(cam.cam_to_world_matrix)
print(cam.world_to_cam_rotation)
print(cam.cam_to_world_rotation)
print(cam.focal_length)
print(cam.principal_point)
print(cam.pixel_aspect)
print(cam.distortion)

print(cam.get_calibration(width=1, height=1))

#cam = v.camera
#print(cam.rotation_matrix)
#print(cam.world_to_cam_matrix)
#print(cam.cam_to_world_matrix)

img = v.get_image('undist-L1')
print(img.data.shape)
print(img.data)
cv2.imshow("show", cv2.cvtColor(img.data, cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
