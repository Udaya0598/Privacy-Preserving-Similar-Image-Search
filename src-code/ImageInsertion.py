from redis import Redis
from nearpy.storage import RedisStorage
from nearpy.hashes import RandomBinaryProjections
from nearpy import Engine
from nearpy.filters import NearestFilter, UniqueFilter
import os
from FeatureExtraction import *
from CryptoUtils import *
from Setup import *

import redis
import pickle

setup_params = Setup()

class ImageInsertion:
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



def __main():
    insertion = ImageInsertion()
    cryptoUtils = CryptoUtils()

    # TODO: read file_path upon triggering the Image inserting GUI
    QUERY_PATH = 'E:/ukbench' + '/query/'
    image_name = "ukbench00032.jpg"
    file_path = QUERY_PATH + image_name

    insertion.set_original_image_path(file_path)
    insertion.set_encrypted_image_path(file_path)
    # image_processing.set_unique_id(Utils.generate_unique_id())
    insertion.set_unique_id(image_name)
    insertion.set_secret_key(cryptoUtils.generate_symmetric_key_K( \
        setup_params.security_parameter))

    print("Original Key: ", insertion.secret_key)
    # Secret key sharing
    shares = CryptoUtils.generate_shares(insertion.secret_key, \
                                         setup_params.sharing_threshold, \
                                         setup_params.num_pieces)

    # index the image in the LHS hash tables

    # Create redis storage adapter
    redis_object = Redis(host='localhost', port=6379, db=0)
    redis_storage = RedisStorage(redis_object)
    lhash_name = 'test-image-retrieval'
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

    engine = Engine(setup_params.engine_dimension, lshashes=[lshash],\
                    vector_filters=[unique, nearest], storage=redis_storage)

    # Feature Extraction from original image using ORB
    feature_extraction = FeatureExtraction()
    descriptors = feature_extraction.orb(file_path, setup_params.num_features)

    if descriptors is not None:
        print('indexing - ' + image_name)
        for i in range(descriptors.shape[0]):
            # While indexing each feature vector, we also store the corresponding image path.
            # So that we can know which image does this feature vector belong to
            engine.store_vector(descriptors[i], image_name)
        redis_storage.store_hash_configuration(lshash)


    # Encrypt shares with the profile vectors
    profile_vectors = dict()
    for i in range(len(descriptors)):
        for bucket_key in lshash.hash_vector(descriptors[i], querying=True):
            profile_vectors[i] = profile_vectors.get(i, "") + bucket_key
            # print('i = %d Bucket %s ', (i, bucket_key))

    # Pieces encryption
    encrypted_shares = CryptoUtils.encrypt_pieces(profile_vectors, shares)

    # Image encryption
    encrypted_image_path, encrypted_image = CryptoUtils.encrypt_image(\
                                                insertion.secret_key,
                                                insertion.original_image_path,
                                                insertion.encrypted_image_path)

   # test code

    # now decrypt the shares with corresponding bucket keys that is profile vectors

    # decrypted_piece = []
    # for i in decrypted_shares.keys():
    #     # Caution: this i+1 is very important, generated shares in
    #     # in the 'Shamir' class starts index from 1, instead from 0
    #     decrypted_piece.append((i + 1, decrypted_shares[i]))
    #     if i == setup_params.sharing_threshold : break
    #
    # reconstructed_key = None
    #
    # try:
    #     reconstructed_key = Shamir.combine(decrypted_piece[0:setup_params.sharing_threshold])
    # except ValueError as e:
    #     print('error type: ', type(e))
    #
    # print("reconstructed key:", reconstructed_key)

    encrypted_record = dict()

    encrypted_record['id'] = insertion.unique_id
    encrypted_record['encrypted_image_path'] = encrypted_image_path
    # encrypted_record['encrypted_image'] = encrypted_image
    encrypted_record['encrypted_shares'] = encrypted_shares
    print(encrypted_record)

    # storing the encrypted record into redis
    p_mydict = pickle.dumps(encrypted_record)
    redis_object.set(insertion.unique_id + '_encrypted', p_mydict)

    # read_dict = redis_object.get(insertion.unique_id + '_encrypted')
    # yourdict = pickle.loads(read_dict)
    # print("after retrieval", yourdict)


if __name__ == '__main__':
    __main()