import numpy as np
import cv2
from matplotlib import pyplot as plt
from CryptoUtils import *
from Crypto.Cipher import AES
from Utils import *
from FeatureExtraction import *
from LocalitySensitiveHashing import *

setup_params = Setup()

# ImageProcessing is done at User side
class ImageProcessing:

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

    def populate_lsh_tables(self, feature_descriptors):
        lsh = LSH(num_tables=setup_params.num_tables,
                  hash_size=setup_params.descriptor_hash_size,
                  inp_dimensions=setup_params.inp_dimensions)
        for i in range(len(feature_descriptors)):
            lsh.__setitem__(feature_descriptors[i], i)
        return lsh

    def generate_profile_vector(self, lsh):

        hash_list_of_feature_vectors = dict()
        for table in lsh.hash_tables:
            for key in table.hash_table.keys():
                feature_vector_indices = table.hash_table[key]

                for index in feature_vector_indices:
                    hash_list_of_feature_vectors[index] = hash_list_of_feature_vectors \
                                                              .get(index, list()) + [key]
        # print(hash_list_of_feature_vectors[0])
        # print(hash_list_of_feature_vectors[1])
        # print(hash_list_of_feature_vectors[2])

        # Profile generation: We apply LSH (k=8, L=32) on each feature vi
        # and get the corresponding profile vector, mi

        # a profile vector of a feature descriptor is the L number of concatenated hash values
        # that is generated from the LSH(k,L), here k is the hash key length of each bucket,
        # and L is the number of tables in the LSH
        # profile_vectors = ["" for x in range(len(hash_list_of_feature_vectors))]
        profile_vectors = dict()
        for key in hash_list_of_feature_vectors:
            for a_hash in hash_list_of_feature_vectors[key]:
                profile_vectors[key] = profile_vectors.get(key, "") + a_hash
        return profile_vectors

    def encrypt_pieces(self, profile_vectors, shares):
        # encrypted_shares = ["" for x in range(setup_params.num_pieces)]
        encrypted_shares = dict()
        idx_cnt = 0
        for descriptor_id in profile_vectors.keys():
            # one-to-one encryption of n number of pieces by n number of profile vectors
            encrypted_shares[descriptor_id] = CryptoUtils.\
                stream_cipher_encrypt(profile_vectors[descriptor_id], shares[idx_cnt][1])
            idx_cnt += 1
            # we are going to decrypt the secret shares upon image retrieval,
            # for now commenting out the decryption
            # decrypted_share = CryptoUtils.stream_cipher_decrypt(profile_vectors[i], encrypted_shares[i])

        return encrypted_shares
    def process(self):

        # Secret key sharing
        shares = CryptoUtils.generate_shares(self.secret_key, \
                                             setup_params.sharing_threshold, \
                                             setup_params.num_pieces)
        # Image encryption
        encrypted_image_path, encrypted_image = CryptoUtils.encrypt_image(self.secret_key,
                                  self.original_image_path)

        # Image decryption (decryption is working) [We will use the decryption after image retrieval]
        # image_processing.set_encrypted_image_path(file_path + ".enc")
        CryptoUtils.decrypt_image(self.secret_key,
                                 encrypted_image_path)

        # Feature Extraction from original image using ORB
        feature_extraction = FeatureExtraction()
        feature_descriptors = feature_extraction.orb(self.original_image_path, \
                                                     setup_params.num_features)

        lsh = self.populate_lsh_tables(feature_descriptors)

        profile_vectors = self.generate_profile_vector(lsh)

        # Pieces encryption
        encrypted_shares = self.encrypt_pieces(profile_vectors, shares)

        return self.unique_id, encrypted_image_path, encrypted_image, encrypted_shares


def __main():

    image_processing = ImageProcessing()
    cryptoUtils = CryptoUtils()

    # TODO: read file_path upon triggering the Image inserting GUI
    directory = "../img/"
    image_name = "ukbench00000.jpg"
    file_path = directory + image_name

    image_processing.set_original_image_path(file_path)
    # image_processing.set_unique_id(Utils.generate_unique_id())
    image_processing.set_unique_id(image_name)
    image_processing.set_secret_key(cryptoUtils.generate_symmetric_key_K(\
        setup_params.security_parameter))

    unique_id, encrypted_image_path, encrypted_image, encrypted_shares = image_processing.process()
    encrypted_record = dict()

    encrypted_record['id'] = unique_id
    encrypted_record['encrypted_image_path'] = encrypted_image_path
    encrypted_record['encrypted_image'] = encrypted_image
    encrypted_record['encrypted_shares'] = encrypted_shares
    print(encrypted_record)

if __name__ == '__main__':
    __main()