from services.ImageUpload import *

class BatchUpload:

    def bluk_upload(self):
        DATASET_PATH = 'E:/ukbench/test'
        ENCRYPTED_FOLDER = '../cloud-server/encrypted'
        upload = ImageUpload()
        # Loop through all the images, and index feature vectors of each image
        for root, dirs, files in os.walk(DATASET_PATH, topdown=False):
            for name in files:
                if 'jpg' in name:
                    absolute_path = os.path.abspath(DATASET_PATH + "/" + name)
                    upload.do_process(DATASET_PATH + "/" + name, name, ENCRYPTED_FOLDER)

def __main():
    upload = BatchUpload()
    upload.bluk_upload()

if __name__ == '__main__':
    __main()