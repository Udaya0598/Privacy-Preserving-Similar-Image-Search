from redis import Redis
from nearpy.storage import RedisStorage
from nearpy.hashes import RandomBinaryProjections
from nearpy import Engine
from nearpy.filters import NearestFilter, UniqueFilter
import os
from FeatureExtraction import *
from Setup import *

class IndexingDataset:
    DATASET_PATH = 'E:/ukbench/full/'

    # this 'dimension' is the projection dimension of LSH,
    # that means, the hash key will be of size = dimension
    dimension = 32

    # indexing the entire dataset once during project initialization
    # Create redis storage adapter
    redis_object = Redis(host='localhost', port=6379, db=0)
    redis_storage = RedisStorage(redis_object)

    # Get hash config from redis
    config = redis_storage.load_hash_configuration('image-retrieval')
    print(config)
    if config is None:
        # Config is not existing, create hash from scratch, with 10 projections
        lshash = RandomBinaryProjections('image-retrieval', dimension)
    else:
        # Config is existing, create hash with None parameters
        lshash = RandomBinaryProjections(None, None)
        # Apply configuration loaded from redis
        lshash.apply_config(config)


    feature_extraction = FeatureExtraction()
    # We are looking for the ten closest neighbours
    nearest = NearestFilter(10)
    # We want unique candidates
    unique = UniqueFilter()
    engine = Engine(dimension, lshashes=[lshash], vector_filters=[unique, nearest], \
                    storage=redis_storage)
    # if config == None:
    print('Indexing all the images')
    # Loop through all the images, and index feature vectors of each image
    for root, dirs, files in os.walk(DATASET_PATH, topdown=False):
        for name in files:
            if 'jpg' in name:
                des = feature_extraction.orb(DATASET_PATH + name, Setup().num_features)

                if des is not None:
                    print('indexing - ' + name)
                    for i in range(des.shape[0]):
                        # While indexing each feature vector, we also store the corresponding image path.
                        # So that we can know which image does this feature vector belong to
                        # engine.store_vector(des[i], DATASET_PATH + name)
                        engine.store_vector(des[i], name)

    redis_storage.store_hash_configuration(lshash)
