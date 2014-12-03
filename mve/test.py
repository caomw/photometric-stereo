import cv2
from mve import Scene
s = Scene()
s.load('../tmp/b-daman')

v = s.views[0]
print(v.camera.principal_point)

img = v.get_image('undist-L1')
print(img.shape)
print(img)
cv2.imshow("show", img)
cv2.waitKey(0)
