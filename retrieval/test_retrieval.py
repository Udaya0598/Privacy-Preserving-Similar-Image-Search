from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

from redis import Redis

from nearpy.storage import RedisStorage
from nearpy.filters import NearestFilter, UniqueFilter
from nearpy.distances import EuclideanDistance
from nearpy.experiments import DistanceRatioExperiment
from CryptoUtils import *

import numpy as np
import cv2
from matplotlib import pyplot as plt
import numpy

import numpy as np
import cv2
from matplotlib import pyplot as plt
import os
from heapq import nsmallest

from FeatureExtraction import *
from Setup import *
import pickle


setup_params = Setup()


do_index = True
# DATASET_PATH = os.getcwd() + '/ukbench/test/'
DATASET_PATH = 'E:/ukbench' + '/test/'

QUERY_PATH = 'E:/ukbench' + '/query/'
query_file_path = QUERY_PATH + 'ukbench00032.jpg'



# Feature Extraction from original image using ORB
feature_extraction = FeatureExtraction()
quer_image_descriptors = feature_extraction.orb(query_file_path, setup_params.num_features)


# this 'dimension' is the projection dimension of LSH,
# that means, the hash key will be of size = dimension
dimension = 32

# Create redis storage adapter
redis_object = Redis(host='localhost', port=6379, db=0)
redis_storage = RedisStorage(redis_object)

# Get hash config from redis
lhash_name = 'test-image-retrieval'

config = redis_storage.load_hash_configuration(lhash_name)

print(config)
if config is None:
    # Config is not existing, create hash from scratch, with 10 projections
    lshash = RandomBinaryProjections(lhash_name, dimension)
else:
    # Config is existing, create hash with None parameters
    lshash = RandomBinaryProjections(None, None)
    # Apply configuration loaded from redis
    lshash.apply_config(config)

# Create engine for feature space of 100 dimensions and use our hash.
# This will set the dimension of the lshash only the first time, not when
# using the configuration loaded from redis. Use redis storage to store
# buckets.

# We are looking for the ten closest neighbours
nearest = NearestFilter(10)
# We want unique candidates
unique = UniqueFilter()


engine = Engine(dimension, lshashes=[lshash], vector_filters=[unique, nearest], storage=redis_storage)
# engine = Engine(dimension, lshashes=[lshash], storage=redis_storage)


feature_descriptor_total_dataset = []
#
# if do_index:
#     print('Indexing all the images')
#     # Loop through all the images, and index feature vectors of each image
#     for root, dirs, files in os.walk(DATASET_PATH, topdown=False):
#         for name in files:
#             if 'jpg' in name:
#                 des = feature_extraction.orb(DATASET_PATH + name, setup_params.num_features)
#
#                 if des is not None:
#                     print('indexing - ' + name)
#                     for i in range(des.shape[0]):
#                         # While indexing each feature vector, we also store the corresponding image path.
#                         # So that we can know which image does this feature vector belong to
#                         feature_descriptor_total_dataset.append(des[i])
#                         # engine.store_vector(des[i], DATASET_PATH + name)
#                         engine.store_vector(des[i], name)
#
#     redis_storage.store_hash_configuration(lshash)

#
# candidates = dict()
# for lshash in engine.lshashes:
#     for i in range(len(quer_image_descriptors)):
#         for bucket_key in lshash.hash_vector(quer_image_descriptors[i], querying=True):
#             bucket_content = engine.storage.get_bucket(lshash.hash_name, bucket_key)
#             # print('i = %d Bucket %s size %d' % (i, bucket_key, len(bucket_content)))
#             if len(bucket_content) >= 10:
#                 candidates[i] = bucket_content
#
#
# popular_descriptors = candidates.keys();
# matched_pair_cnt = dict()
# for descriptor_idx in popular_descriptors:
#     a_bucket = candidates.get(descriptor_idx)
#     for each_item in a_bucket:
#         descriptor = each_item[0]
#         image_identifier = each_item[1]
#
#         matched_pair_cnt[image_identifier] = \
#             matched_pair_cnt.get(image_identifier, 0) + 1


# Querying

# Loop through each feature vector of query image and extract
# neigbours for each feature vector
"""
  Hashes vector v, collects all candidate vectors from the matching
  buckets in storage, applys the (optional) distance function and
  finally the (optional) filter function to construct the returned list
  of either (vector, data, distance) tuples or (vector, data) tuples.
"""
results = dict()
for i in range(quer_image_descriptors.shape[0]):
    nbs = engine.neighbours(quer_image_descriptors[i])
    # shape of nbs is (vector, data, distance)
    results[i] = nbs


all_feature_id = results.keys();
feature_wise_cumulative_dist = dict()
for descriptor_idx in all_feature_id:
    a_bucket = results.get(descriptor_idx)
    for each_item in a_bucket:
        descriptor = each_item[0]
        image_identifier = each_item[1]
        distance = each_item[2]

        feature_wise_cumulative_dist[image_identifier] = \
            feature_wise_cumulative_dist.get(image_identifier, 0) + distance

nn_distance = min(feature_wise_cumulative_dist.values())
nearest_neighbor_id = min(feature_wise_cumulative_dist, key=feature_wise_cumulative_dist.get)

print("Min distance: ", nn_distance)
print("the image ID ", nearest_neighbor_id)

res = nsmallest(4, feature_wise_cumulative_dist, key = feature_wise_cumulative_dist.get)

# printing result
print("The minimum K value pairs are " + str(res))

# retrieve the encrypted record from the cloud server
read_dict = redis_object.get(nearest_neighbor_id + '_encrypted')
encrypted_record = pickle.loads(read_dict)
print("after retrieval", encrypted_record)

image_name = encrypted_record['id']
encrypted_image_path = encrypted_record['encrypted_image_path']
encrypted_shares = encrypted_record['encrypted_shares']
print(encrypted_record)

# Encrypt shares with the profile vectors
profile_vectors = dict()
for i in range(len(quer_image_descriptors)):
    for bucket_key in lshash.hash_vector(quer_image_descriptors[i], querying=True):
        profile_vectors[i] = profile_vectors.get(i, "") + bucket_key
        # print('i = %d Bucket %s ', (i, bucket_key))


# now decrypt the shares with corresponding bucket keys that is profile vectors
decrypted_shares = CryptoUtils.decrypt_pieces(profile_vectors, encrypted_shares)

user_pieces = []
for i in range(len(decrypted_shares)):
    user_pieces.append((i + 1, decrypted_shares[i][1]))
    if i+1 == setup_params.sharing_threshold : break

reconstructed_key = Shamir.combine(user_pieces)
print("reconstructed key:", reconstructed_key)
CryptoUtils.decrypt_image(reconstructed_key, encrypted_image_path, encrypted_image_path)