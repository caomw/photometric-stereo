# python setup.py build_ext --inplace
import cv2
from mve import Scene
s = Scene()
s.load('../tmp/b-daman')

v = s.views[0]

cam = v.camera
print(cam.principal_point)
print(cam.translation_vector)
print(cam.rotation_matrix)

img = v.get_image('undist-L1')
print(img.shape)
#print(img)
cv2.imshow("show", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
