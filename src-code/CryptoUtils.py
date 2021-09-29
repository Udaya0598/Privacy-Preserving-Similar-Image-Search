from binascii import hexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Random import random
from Crypto.Protocol.SecretSharing import Shamir
import secrets
from binascii import unhexlify

from Crypto.Util.number import long_to_bytes
from Crypto.Cipher import ChaCha20
from base64 import b64encode
from base64 import b64decode
import os, struct
# import pyAesCrypt

import random
from Setup import *

class CryptoUtils:

    @staticmethod
    def byte_xor(ba1, ba2):
        return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

    @staticmethod
    def bitstring_to_bytes(s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

    @staticmethod
    def generate_symmetric_key_K(security_parameter):
        return get_random_bytes(security_parameter)

    @staticmethod
    def stream_cipher_encrypt(k, s):
        random.seed(k)
        v = random.getrandbits(8 * len(s)) # sk(ij)
        # print("Psuedo random number(enc): ",v)
        u = long_to_bytes(v)
        return CryptoUtils.byte_xor(u, s)

    @staticmethod
    def stream_cipher_decrypt(k, s):
        random.seed(k)
        v = random.getrandbits(8 * len(s))
        # print("Psuedo random number(dec): ", v)
        u = long_to_bytes(v)
        return CryptoUtils.byte_xor(u, s)

    def encrypt_stream_cipher(self, profile_vector, share):
        byte_array = CryptoUtils.bitstring_to_bytes(profile_vector)
        cipher = ChaCha20.new(key=byte_array)
        ciphertext = cipher.encrypt(share)
        nonce = b64encode(cipher.nonce).decode('utf-8')
        ct = b64encode(ciphertext).decode('utf-8')
        return ct, nonce

    def decrypt_stream_cipher(self, profile_vector, share, nonce):
        nonce = b64decode(nonce)
        ciphertext = b64decode(share)
        byte_array = CryptoUtils.bitstring_to_bytes(profile_vector)
        cipher = ChaCha20.new(key=byte_array, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext

    @staticmethod
    def encrypt_pieces(profile_vectors, shares):
        encrypted_shares = dict()
        # decrypted_shares = dict()
        idx_cnt = 0
        for descriptor_id in profile_vectors.keys():
            # one-to-one encryption of n number of pieces by n number of profile vectors
            encrypted_shares[descriptor_id] = CryptoUtils.\
                stream_cipher_encrypt(profile_vectors[descriptor_id], shares[idx_cnt][1])

            # we are going to decrypt the secret shares upon image retrieval,
            # for now commenting out the decryption
            # decrypted_shares[idx_cnt] = CryptoUtils.stream_cipher_decrypt(profile_vectors[descriptor_id], encrypted_shares[descriptor_id])
            # print("plain share : ", shares[idx_cnt][1])
            # print("encrypted share : ", encrypted_shares[descriptor_id])
            # print("decrypted share : ", decrypted_share)

            # if shares[idx_cnt][1] == decrypted_shares[idx_cnt]:
            #     print("success")
            # else:
            #     print("Failed")

            idx_cnt += 1
        # return encrypted_shares, decrypted_shares
        return encrypted_shares

    @staticmethod
    def decrypt_pieces(profile_vectors, encrypted_shares):
        # encrypted_shares = ["" for x in range(setup_params.num_pieces)]
        decrypted_shares = []

        for descriptor_id in profile_vectors.keys():
            # one-to-one decryption of n number of pieces by n number of profile vectors
            # decrypted_share = unhexlify(CryptoUtils.stream_cipher_decrypt(profile_vectors[descriptor_id], encrypted_shares[descriptor_id]))
            decrypted_share = CryptoUtils.stream_cipher_decrypt(profile_vectors[descriptor_id], encrypted_shares[descriptor_id])
            decrypted_shares.append((descriptor_id, decrypted_share))

        return decrypted_shares

    def encrypt(self):
        key = get_random_bytes(16)
        print("Original Key  %s" % (key))
        shares = Shamir.split(2, 5, key)
        for idx, share in shares:
            print ("Index #%d: %s" % (idx, hexlify(share)))

        with open("clear.txt", "rb") as fi, open("enc.txt", "wb") as fo:
            cipher = AES.new(key, AES.MODE_EAX)
            ct, tag = cipher.encrypt(fi.read()), cipher.digest()
            fo.write( cipher.nonce + tag + ct)

    def combine(self):
        shares = []

        idx1 = 1
        share1 =  unhexlify(b'b6a49e6be9b0026f50426537bdd3a5f9')
        idx2 = 2
        share2 =  unhexlify(b'df12cabf5979e9a8f5d55f66685a2ce7')

        shares.append((idx1, share1))
        shares.append((idx2, share2))

        key = Shamir.combine(shares)

        print("reconstructed key: ", key)
        with open("enc.txt", "rb") as fi:
            nonce, tag = [fi.read(16) for x in range(2)]
            cipher = AES.new(key, AES.MODE_EAX, nonce)
            try:
                result = cipher.decrypt(fi.read())
                print(result)
                cipher.verify(tag)
                with open("clear2.txt", "wb") as fo:
                    fo.write(result)
            except ValueError:
                print("The shares were incorrect")


    @staticmethod
    def generate_shares(key, sharing_threshold, no_of_pieces):
        # key = get_random_bytes(16)
        # print("Key  %s" % (key))
        shares = Shamir.split(sharing_threshold, no_of_pieces, key)
        # for idx, share in shares:
        #     print("Index #%d: %s" % (idx, hexlify(share)))

        return shares

    @staticmethod
    def encrypt_image(key, in_filename, out_filename):
        """ Encrypts a file using AES (CBC mode) with the
            given key.

            key:
                The encryption key - a string that must be
                either 16, 24 or 32 bytes long. Longer keys
                are more secure.

            in_filename:
                Name of the input file

            out_filename:
                If None, '<in_filename>.enc' will be used.

            chunksize:
                Sets the size of the chunk which the function
                uses to read and encrypt the file. Larger chunk
                sizes can be faster for some files and machines.
                chunksize must be divisible by 16.
        """
        chunksize = 64 * 1024
        out_filename = out_filename + ".enc"

        # iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        iv = get_random_bytes(Setup().security_parameter)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        padding_length = 16 - (len(chunk) % 16)
                        chunk += bytes([padding_length]) * padding_length
                        # chunk += ' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))
        return out_filename, outfile

    @staticmethod
    def decrypt_image(key, in_filename, out_filename):
        """ Decrypts a file using AES (CBC mode) with the
            given key. Parameters are similar to encrypt_file,
            with one difference: out_filename, if not supplied
            will be in_filename without its last extension
            (i.e. if in_filename is 'aaa.zip.enc' then
            out_filename will be 'aaa.zip')
        """
        chunksize = 64 * 1024
        # out_filename = in_filename + ".dec"

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)

def __main():
    encryption =  CryptoUtils()
    encryption.encrypt()
    # encryption.combine()



if __name__ == '__main__':
    __main()