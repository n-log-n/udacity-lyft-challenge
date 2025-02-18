import sys
import glob
import numpy as np
import skvideo.io
import json, base64
from PIL import Image
from io import BytesIO, StringIO
from skimage.io import imread

def encode(array):
  pil_img = Image.fromarray(array)
  buff = BytesIO()
  pil_img.save(buff, format="PNG")
  return base64.b64encode(buff.getvalue()).decode("utf-8")

if len(sys.argv) < 1:
  print ("Missing argument: python %s path", sys.argv[0])

path = sys.argv[1]
files = glob.glob("%s/CameraRGB/*.png"%path)
files.sort()

tmp = imread(files[0])
m = len(files)

# data = np.empty((m, *tmp.shape))

data = []
for ind, file in enumerate(files):
  data.append(imread(file))

skvideo.io.vwrite("video.mp4", np.array(data))

files = glob.glob("%s/CameraSeg/*.png"%path)
files.sort()

truth_key = {}
frame = 1

for ind, file in enumerate(files):
  img = imread(file)[:, :, 0]

  lane_marking_pixels = (img == 6).nonzero()
  # Set lane marking pixels to road (label is 7)
  img[lane_marking_pixels] = 7

  # Identify all vehicle pixels
  vehicle_pixels = (img == 10).nonzero()
  # Isolate vehicle pixels associated with the hood (y-position > 496)
  hood_indices = (vehicle_pixels[0] >= 496).nonzero()[0]
  hood_pixels = (vehicle_pixels[0][hood_indices], \
                   vehicle_pixels[1][hood_indices])
  # Set hood pixel labels to 0
  img[hood_pixels] = 0

  car = np.zeros_like(img)
  road = np.zeros_like(img)

  car = (img == 10).astype(np.uint8)
  road = (img == 7).astype(np.uint8)
  
  truth_key[frame] = [encode(car), encode(road)] 
  frame += 1

print (json.dumps(truth_key))


