
class Setup:
    def __init__(self):
        self.debug = False
        self.evaluate = True
        self.generate_evaluation_plot = False
        self.do_indexing = False
        self.security_parameter = 16    # security_parameter, λ
        #NOTE: do not make the sharing_threshold grater than 20
        self.sharing_threshold = 20      # threshold value for secret sharing, m
        self.num_pieces = 120          # pieces number must be equal
        self.num_features = 120        # pieces number must be equal
        self.num_hashtable = 120
        self.num_tables = 32
        self.descriptor_hash_size = 8
        self.inp_dimensions = 32        # this is the column count of each feature descriptors
        self.engine_dimension = 32      # this is the dimension required to instantiate an Nearpy engine
        self.lhash_name = 'test-image-retrieval'



