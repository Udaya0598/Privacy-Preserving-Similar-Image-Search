import cv2

class FeatureExtraction:
    def orb(self, file_path, no_of_features):
        img = cv2.imread(file_path, 0)

        # Initiate ORB detector
        orb = cv2.ORB_create(nfeatures=no_of_features)
        # find the keypoints with ORB
        kp = orb.detect(img, None)
        # compute the descriptors with ORB
        kp, des = orb.compute(img, kp)
        # print("DEscriptor: ",des)
        return des

        # star = cv2.xfeatures2d.StarDetector_create()
        # brief = cv2.xfeatures2d.BriefDescriptorExtractor_create(bytes=32, use_orientation=False)
        #
        # kp = star.detect(img, None)
        # kp, quer_image_descriptors = brief.compute(img, kp)
        # return quer_image_descriptors[0:120]