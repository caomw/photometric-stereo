from os.path import dirname, abspath, join, exists
import sys 
ROOT_PATH = dirname(abspath(__file__))
sys.path.append(join(ROOT_PATH, 'mve'))
sys.path.append(join(ROOT_PATH, 'plyfile'))
from mve.core import Scene
from argparse import ArgumentParser

parser = ArgumentParser(description='Find Valid Views')
parser.add_argument('scene', help='Scene Directory')
ARGS = parser.parse_args()

# Load Scene
print('Scene: ' + ARGS.scene)
SCENE = Scene()
SCENE.load(ARGS.scene)

views = SCENE.views
for v in views:
    if v.camera_valid:
        print(v.id)
