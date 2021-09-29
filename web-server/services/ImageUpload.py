from redis import Redis
from nearpy.storage import RedisStorage
from nearpy.hashes import RandomBinaryProjections
from nearpy import Engine
from nearpy.filters import NearestFilter, UniqueFilter
import os
from FeatureExtraction import *
from CryptoUtils import *
from Setup import *
import time

import redis
import pickle

setup_params = Setup()

class ImageUpload:
    def __init__(self):
        self.original_image_path = None
        self.unique_id = None
        self.encrypted_image_path = None
        self.secret_key = None

    def set_original_image_path(self, file_path):
        self.original_image_path = file_path

    def set_unique_id(self, id):
        self.unique_id = id

    def set_encrypted_image_path(self, encrypted_image_path):
        self.encrypted_image_path = encrypted_image_path

    def set_secret_key(self, key):
        self.secret_key = key


    def do_process(self, original_file_path, image_name, enc_file_path ):

        key_list = ['key_processing','feature_vector',
                       'profile_vector','indexing',
                       'image_encryption', 'storage']

        computation_time = dict.fromkeys(key_list, 0)

        start_time = time.time()
        cryptoUtils = CryptoUtils()

        self.set_original_image_path(original_file_path)
        # image_processing.set_unique_id(Utils.generate_unique_id())
        self.set_unique_id(image_name)
        self.set_secret_key(cryptoUtils.generate_symmetric_key_K( \
            setup_params.security_parameter))
        self.set_encrypted_image_path(enc_file_path)

        print("Uploaded Image: ", image_name, " ---> Original Key, K: ", self.secret_key)
        # Secret key sharing
        shares = CryptoUtils.generate_shares(self.secret_key, \
                                             setup_params.sharing_threshold, \
                                             setup_params.num_pieces)

        if setup_params.debug and len(shares) > 0:
            print("A single plain share, pi: ", shares[0][1])

        computation_time['key_processing'] = time.time() - start_time

        indexing_start_time = time.time()

        # index the image in the LHS hash tables
        # Create redis storage adapter
        redis_object = Redis(host='localhost', port=6379, db=0)
        redis_storage = RedisStorage(redis_object)
        lhash_name = setup_params.lhash_name
        # Get hash config from redis
        config = redis_storage.load_hash_configuration(lhash_name)
        # Get hash config from redis
        config = redis_storage.load_hash_configuration(lhash_name)
        if config is None:
            # Config is not existing, create hash from scratch, with 10 projections
            lshash = RandomBinaryProjections(lhash_name, setup_params.engine_dimension)
        else:
            # Config is existing, create hash with None parameters
            lshash = RandomBinaryProjections(None, None)
            # Apply configuration loaded from redis
            lshash.apply_config(config)
        # We are looking for the ten closest neighbours
        nearest = NearestFilter(10)
        # We want unique candidates
        unique = UniqueFilter()

        engine = Engine(setup_params.engine_dimension, lshashes=[lshash], \
                        vector_filters=[unique, nearest], storage=redis_storage)



        feature_start_time = time.time()

        # Feature Extraction from original image using ORB
        feature_extraction = FeatureExtraction()
        descriptors = feature_extraction.orb(original_file_path, setup_params.num_features)

        if setup_params.debug and len(descriptors) > 0:
            print("A single feature vector, vi: ", descriptors[0])

        computation_time['feature_vector'] = time.time() - feature_start_time

        if descriptors is not None:
            # print('indexing - ' + image_name)
            for i in range(descriptors.shape[0]):
                # While indexing each feature vector, we also store the corresponding image path.
                # So that we can know which image does this feature vector belong to
                engine.store_vector(descriptors[i], image_name)
            redis_storage.store_hash_configuration(lshash)

        computation_time['indexing'] = time.time() - indexing_start_time

        start_time = time.time()
        # Encrypt shares with the profile vectors
        profile_vectors = dict()
        for i in range(len(descriptors)):
            for bucket_key in lshash.hash_vector(descriptors[i], querying=True):
                profile_vectors[i] = profile_vectors.get(i, "") + bucket_key
                # print('i = %d Bucket %s ', (i, bucket_key))

        if setup_params.debug and len(profile_vectors) > 0:
            print("A single profile_vector, mi: ", profile_vectors[0])

        computation_time['profile_vector'] = time.time() - start_time

        start_time = time.time()
        # Pieces encryption
        encrypted_shares = CryptoUtils.encrypt_pieces(profile_vectors, shares)
        computation_time['key_processing'] += time.time() - start_time

        if setup_params.debug and len(encrypted_shares) > 0:
            print("A single encrypted share : ", encrypted_shares[0])

        start_time = time.time()
        # Image encryption
        encrypted_image_path, encrypted_image = CryptoUtils.encrypt_image( \
            self.secret_key,
            self.original_image_path,
            self.encrypted_image_path + "/" + image_name)

        computation_time['image_encryption'] = time.time() - start_time

        start_time = time.time()
        encrypted_record = dict()

        encrypted_record['id'] = self.unique_id
        encrypted_record['encrypted_image_path'] = encrypted_image_path
        # encrypted_record['encrypted_image'] = encrypted_image
        encrypted_record['encrypted_shares'] = encrypted_shares
        encrypted_record['nonce'] = self.secret_key,

        # storing the encrypted record into redis
        p_mydict = pickle.dumps(encrypted_record)
        redis_object.set(self.unique_id + '_encrypted', p_mydict)
        computation_time['storage'] = time.time() - start_time
        return computation_time
def __main():
    upload = ImageUpload()
    upload.do_process()

if __name__ == '__main__':
    __main()