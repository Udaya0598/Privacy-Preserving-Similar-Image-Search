# https://towardsdatascience.com/locality-sensitive-hashing-for-music-search-f2f1940ace23

import numpy as np
from ImageProcessing import *
from FeatureExtraction import *
from Setup import *

setup_params = Setup()

class HashTable:
    def __init__(self, hash_size, inp_dimensions):
        self.hash_size = hash_size
        self.inp_dimensions = inp_dimensions
        self.hash_table = dict()
        self.projections = np.random.randn(self.hash_size, inp_dimensions)


    def generate_hash(self, inp_vector):
        bools = (np.dot(inp_vector, self.projections.T) > 0).astype('int')
        return ''.join(bools.astype('str'))

    def __setitem__(self, inp_vec, label):
        hash_value = self.generate_hash(inp_vec)
        self.hash_table[hash_value] = self.hash_table.get(hash_value, list()) + [label]

    def __getitem__(self, inp_vec):
        hash_value = self.generate_hash(inp_vec)
        return self.hash_table.get(hash_value, [])


class LSH:
    def __init__(self, num_tables, hash_size, inp_dimensions):
        self.num_tables = num_tables
        self.hash_size = hash_size
        self.inp_dimensions = inp_dimensions
        self.hash_tables = list()
        for i in range(self.num_tables):
            self.hash_tables.append(HashTable(self.hash_size, self.inp_dimensions))

    def __setitem__(self, inp_vec, label):
        for table in self.hash_tables:
            table[inp_vec] = label

    def __getitem__(self, inp_vec):
        results = list()
        for table in self.hash_tables:
            results.extend(table[inp_vec])
        return list(set(results))


def __main():
    feature_extraction = FeatureExtraction()
    file_path = "../img/ukbench00000.jpg"
    feature_descriptors = feature_extraction.orb(file_path, Setup().num_features)

    lsh = LSH(num_tables=32, hash_size=8, inp_dimensions=32)


    for i in range(len(feature_descriptors)):
        lsh.__setitem__(feature_descriptors[i], i)

    for i in range(len(feature_descriptors)):
        print("The %d descriptor: %s: \n" % (i, feature_descriptors[i]))
        print("The descriptor from Htable is %s \n" % (lsh\
                                                       .__getitem__(feature_descriptors[i])))
    hash_list_of_feature_vectors = dict()
    for table in lsh.hash_tables:
        for key in table.hash_table.keys():
            feature_vector_indices = table.hash_table[key]

            for index in feature_vector_indices:
                hash_list_of_feature_vectors[index] = hash_list_of_feature_vectors\
                                                          .get(index, list()) + [key]

    print(hash_list_of_feature_vectors[0])
    print(hash_list_of_feature_vectors[1])
    print(hash_list_of_feature_vectors[2])

    feature_hased = ["" for x in range(len(hash_list_of_feature_vectors))]
    for key in hash_list_of_feature_vectors:
        for a_hash in hash_list_of_feature_vectors[key]:
            feature_hased[key] = feature_hased[key] + a_hash


    cryptoUtils =  CryptoUtils()
    key = cryptoUtils.generate_symmetric_key_K(setup_params.security_parameter)
    sharing_threshold = setup_params.sharing_threshold
    no_of_pieces = setup_params.num_pieces
    shares = cryptoUtils.generate_shares(key, sharing_threshold, no_of_pieces)

    plain_share = shares[0][1]
    encrypted_share = cryptoUtils.stream_cipher_encrypt(feature_hased[0], plain_share)
    decrypted_share = cryptoUtils.stream_cipher_decrypt(feature_hased[0], encrypted_share)

    print("Plain share: ", plain_share)
    print("encrypted_share: ", encrypted_share)
    print("decrypted_share: ", decrypted_share)

    if plain_share != decrypted_share:
        print("Plaintext is not matching up")
    else:
        print("Successful Encryption-Decryption")

    # We we are not going to use ChaCha20 as it uses nonce,
    # and in our case use since we do not want to share the
    # symmetric key and so there is no way to share the nonce either.
    # One more freedom to NOT use ChaCha20 for stream cipher is that
    # it strictly requires a 32-byte symmetric key

    # encrypted_share_stream, nonce = cryptoUtils.encrypt_stream_cipher(\
    #     feature_hased[0], plain_share)
    # decrypted_share_stream = cryptoUtils.decrypt_stream_cipher(\
    #     feature_hased[0], encrypted_share_stream, nonce)
    #
    # print("Plain share: ", plain_share)
    # print("stream cipher encrypted_share: ", encrypted_share_stream)
    # print("stream cipher decrypted_share: ", decrypted_share_stream)
    #
    # if plain_share != decrypted_share:
    #     print("Plaintext is not matching up")
    # else:
    #     print("Successful Encryption-Decryption")

if __name__ == '__main__':
    __main()
