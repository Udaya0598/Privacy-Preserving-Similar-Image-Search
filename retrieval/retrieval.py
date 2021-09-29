from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

from redis import Redis

from nearpy.storage import RedisStorage

import numpy as np
import cv2
from matplotlib import pyplot as plt
import numpy

import numpy as np
import cv2
from matplotlib import pyplot as plt
import os

DATASET_PATH = os.getcwd() + '/ukbench/test/'

print DATASET_PATH

query_image = cv2.imread(DATASET_PATH + 'ukbench00000.jpg',0)

star = cv2.xfeatures2d.StarDetector_create()
brief = cv2.xfeatures2d.BriefDescriptorExtractor_create(bytes=32, use_orientation=False)

kp = star.detect(query_image,None)
kp, quer_image_descriptors = brief.compute(query_image, kp)


print quer_image_descriptors
# [[ 31 133 176 ... 119 192 169]
#  [180 102  49 ...  66 123  46]
#  [ 94 207 128 ... 117 237  43]
#  ...
#  [ 27   7 184 ...   5  96 218]
#  [176 247 127 ... 157  65  30]
#  [229 187 147 ... 183 191   0]]

dimension = 32


# Create redis storage adapter
redis_object = Redis(host='localhost', port=6379, db=0)
redis_storage = RedisStorage(redis_object)

# Get hash config from redis
config = redis_storage.load_hash_configuration('image-retrieval')


print config
if config is None:
    # Config is not existing, create hash from scratch, with 10 projections
    lshash = RandomBinaryProjections('image-retrieval', 32)
else:
    # Config is existing, create hash with None parameters
    lshash = RandomBinaryProjections(None, None)
    # Apply configuration loaded from redis
    lshash.apply_config(config)

# Create engine for feature space of 100 dimensions and use our hash.
# This will set the dimension of the lshash only the first time, not when
# using the configuration loaded from redis. Use redis storage to store
# buckets.

engine = Engine(dimension, lshashes=[lshash], storage=redis_storage)


# Loop through all the images, and index feature vectors of each image
for root, dirs, files in os.walk(DATASET_PATH, topdown=False):
    for name in files:
        if 'jpg' in name:
            img = cv2.imread(DATASET_PATH + name,0)
            kp = star.detect(img,None)
            kp, des = brief.compute(img, kp)

            if des is not None:
                print 'indexing - ' + name
                for i in range(des.shape[0]):
                    # While indexing each feature vector, we also store the corresponding image path.
                    # So that we can know which image does this feature vector belong to
                    engine.store_vector(des[i], DATASET_PATH + name)

results = []


# Querying

# Loop through each feature vector of query image and extract neigbours for each feature vector
"""
  Hashes vector v, collects all candidate vectors from the matching
  buckets in storage, applys the (optional) distance function and
  finally the (optional) filter function to construct the returned list
  of either (vector, data, distance) tuples or (vector, data) tuples.
"""

for i in range(quer_image_descriptors.shape[0]):
    nbs = engine.neighbours(quer_image_descriptors[i])
    # shape of nbs is (vector, data, distance)
    results.extend(nbs)

avgs = {}

for result_index in range(len(results)):
    result = results[result_index]
    path = result[1]
    if path in avgs:
        avgs[path] = {
            'total_feature_vectors_matched': avgs[path]['total'] + 1,
        }
    else:
        obj = {
                "total_feature_vectors_matched" : 1,
            }
        avgs[path] = obj

print '-------------- Results --------------'
print avgs
