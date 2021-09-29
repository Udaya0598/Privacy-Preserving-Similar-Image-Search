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
import time


setup_params = Setup()

class ImageSearchAndRetrieve:


    def do_process(self, query_file_path, query_image_name, dec_file_path):

        key_list = ['feature_vector', 'profile_vector',
                       'search', 'retrieval',
                       'key_reconstruction',
                       'decryption']

        computation_time = dict.fromkeys(key_list, 0)

        start_time = time.time()
        # Feature Extraction from original image using ORB
        feature_extraction = FeatureExtraction()
        quer_image_descriptors = feature_extraction.orb(query_file_path, setup_params.num_features)

        if setup_params.debug and len(quer_image_descriptors) > 0:
            print("A single feature vector, vi: ", quer_image_descriptors[0])

        computation_time['feature_vector'] = time.time() - start_time
        start_time = time.time()
        # this 'dimension' is the projection dimension of LSH,
        # that means, the hash key will be of size = dimension
        dimension = 32

        # Create redis storage adapter
        redis_object = Redis(host='localhost', port=6379, db=0)
        redis_storage = RedisStorage(redis_object)

        # Get hash config from redis
        lhash_name = setup_params.lhash_name

        config = redis_storage.load_hash_configuration(lhash_name)

        # print(config)
        if config is None:
            # Config is not existing, create hash from scratch, with 10 projections
            lshash = RandomBinaryProjections(lhash_name, dimension)
        else:
            # Config is existing, create hash with None parameters
            lshash = RandomBinaryProjections(None, None)
            # Apply configuration loaded from redis
            lshash.apply_config(config)

        # We are looking for the ten closest neighbours
        nearest = NearestFilter(10)
        # We want unique candidates
        unique = UniqueFilter()

        engine = Engine(dimension, lshashes=[lshash], vector_filters=[unique, nearest], storage=redis_storage)
        # engine = Engine(dimension, lshashes=[lshash], storage=redis_storage)

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

        # finding the smallest distance
        # nn_distance = min(feature_wise_cumulative_dist.values())
        # print("Min distance: ", nn_distance)

        # finding the most similar images with highest matching in feature vectors
        nearest_neighbor_id = min(feature_wise_cumulative_dist, key=feature_wise_cumulative_dist.get)

        print("Query image ", query_image_name)
        # print("Closest matching ", nearest_neighbor_id)

        # finding 4 closest matching images
        res = nsmallest(4, feature_wise_cumulative_dist, key=feature_wise_cumulative_dist.get)

        # printing result
        print("Closest 4 matching images" + str(res))

        computation_time['search'] = time.time() - start_time
        start_time = time.time()
        # Decrypt shares with the profile vectors
        profile_vectors = dict()
        for i in range(len(quer_image_descriptors)):
            for bucket_key in lshash.hash_vector(quer_image_descriptors[i], querying=True):
                profile_vectors[i] = profile_vectors.get(i, "") + bucket_key
                # print('i = %d Bucket %s ', (i, bucket_key))

        computation_time['profile_vector'] = time.time() - start_time

        if setup_params.debug and len(profile_vectors) > 0:
            print("A single profile_vector, mi: ", profile_vectors[0])

        # Evaluating Accuracy
        item_found = False
        similar_image_serials = []
        resulting_image_serials = []
        ground_thruth_images = []
        #find the serial from the query image name
        image_serial_number = int((query_image_name.split('.')[0])[7:], base=10)
        offset = image_serial_number % 4
        for m in range(4):
            similar_image_serials.append(m + image_serial_number - offset)
            # resulting_image_serials.append(int((res[m].split('.')[0])[7:], base=10))

        for n in range(len(res)):
            resulting_image_serials.append(int((res[n].split('.')[0])[7:], base=10))

        intersection_list = list(set(similar_image_serials) & set(resulting_image_serials))

        if len(intersection_list) > 0:
            item_found = True
            print("Item found!")
        else: print("Item Not found!")

        # retrieve all the encrypted records from the search result
        for index in range(len(res)):
            st = time.time()
            read_dict = redis_object.get(res[index] + '_encrypted')
            encrypted_record = pickle.loads(read_dict)
            # print("after retrieval", encrypted_record)

            retrieved_image_name = encrypted_record['id']
            encrypted_image_path = encrypted_record['encrypted_image_path']
            encrypted_shares = encrypted_record['encrypted_shares']
            nonce = encrypted_record['nonce'][0]
            computation_time['retrieval'] += time.time() - st

            resonstruction_time = time.time()

            # now decrypt the shares with corresponding bucket keys that is profile vectors
            decrypted_shares = CryptoUtils.decrypt_pieces(profile_vectors, encrypted_shares)

            if setup_params.debug and len(decrypted_shares) > 0:
                print("A single decrypted share : ", decrypted_shares[0])

            user_pieces = []
            for i in range(len(decrypted_shares)):
                user_pieces.append((i + 1, decrypted_shares[i][1]))
                if i + 1 == setup_params.sharing_threshold: break

            # reconstructed_key = Shamir.combine(user_pieces)
            computation_time['key_reconstruction'] = time.time() - resonstruction_time


            if setup_params.debug and nonce:
                print("The decrypted key, K : ", nonce)
            # print("reconstructed Key of ", retrieved_image_name,  " : ", nonce)

            start_time = time.time()
            CryptoUtils.decrypt_image(nonce,
                                      encrypted_image_path,
                                      dec_file_path + "/" + retrieved_image_name)

            computation_time['decryption'] = time.time() - start_time
        return res, item_found, computation_time

def __main():

    search = ImageSearchAndRetrieve()
    # query_file_path = '../cloud_server/images/ukbench00018.jpg'
    # query_image_name = 'ukbench00018.jpg'
    # dec_file_path = '../cloud_server/decrypted'
    # search.do_process(query_file_path, query_image_name, dec_file_path)


if __name__ == '__main__':
    __main()
