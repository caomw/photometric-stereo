# python setup.py build_ext --inplace
import cv2
from mve.core import Scene
s = Scene()
s.load('../tmp/b-daman/scene')
#s.load(0)

views = s.get_views()
print(views)

v = views[1]
print(v)

#cam = v.camera
#print(cam)

#cam = v.camera
#print(cam.principal_point)
#print(cam.translation_vector)
#print(cam.rotation_matrix)
#print(cam.world_to_cam_matrix)
#print(cam.cam_to_world_matrix)

#img = v.get_image('undist-L1')
#print(img.raw)
#print(img)
#cv2.imshow("show", cv2.cvtColor(img.raw, cv2.COLOR_RGB2BGR))
#cv2.waitKey(0)
