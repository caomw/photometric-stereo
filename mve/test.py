# python setup.py build_ext --inplace
import cv2
from mve.core import Scene
s = Scene()
s.load('../tmp/daibutsu/scene')
#s.load(0)

views = s.views

for view in views:
    #print(view.id)
    cam = view.camera
    #if not view.valid:
    #    print("View[{}] has invalid camera".format(view.id))
    #print('View[{}]: CamPos = {}'.format(view.id, cam.position))
    #print(cam.translation)
    #print(cam.view_dir)
    #print(cam.world_to_cam_matrix)
    #print(cam.cam_to_world_matrix)
    #print(cam.world_to_cam_rotation)
    #print(cam.cam_to_world_rotation)
    #print(cam.focal_length)
    #print(cam.principal_point)
    #print(cam.pixel_aspect)
    #print(cam.distortion)
    #print(cam.get_calibration(width=1, height=1))
    img = view.get_image('undist-L1')
    if img is not None:
        cv2.imshow("show", cv2.cvtColor(img.data, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)
    else:
        print("View[{}] has no image".format(view.id))
    view.cleanup_cache()
