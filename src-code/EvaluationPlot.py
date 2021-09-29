import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class EvaluationPlot:
    def __init__(self):
        print("")

    def draw_image_upload_timing(self, computation_time, total_time):
        formatter = "{0:.3f}"
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_axes([0, 0, 1, 1])
        sub_modules = ['key_processing','feature_vector',
                       'profile_vector','indexing',
                       'image_encryption', 'storage']
        processing_time = [computation_time['key_processing'],
                           computation_time['feature_vector'],
                           computation_time['profile_vector'],
                           computation_time['indexing'],
                           computation_time['image_encryption'],
                           computation_time['storage'],
                           ]
        processing_time_str = [formatter.format(computation_time['key_processing']),
                           formatter.format(computation_time['feature_vector']),
                           formatter.format(computation_time['profile_vector']),
                           formatter.format(computation_time['indexing']),
                           formatter.format(computation_time['image_encryption']),
                           formatter.format(computation_time['storage']),
                           ]
        df = pd.DataFrame({"Processing time (sec)": processing_time,
                           "Computation steps": sub_modules})
        sns.barplot(x='Computation steps', y="Processing time (sec)", data=df)
        # ax.bar(sub_modules, processing_time_str)
        # ax.set_ylabel('Processing time (sec)', fontsize=12)
        # ax.set_xlabel('Computation steps', fontsize=12)
        ax.set_title('The total time: '+ formatter.format(total_time)+' sec')

        plt.savefig('plot/upload.png', dpi=200, format='png', bbox_inches='tight')
        # plt.show()
        plt.clf()

    def draw_image_search_timing(self, computation_time, total_time):
        formatter = "{0:.3f}"
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_axes([0, 0, 1, 1])

        sub_modules = ['feature_vector', 'profile_vector',
                       'search', 'retrieval',
                       'key_reconstruction',
                       'decryption']
        processing_time = [computation_time['feature_vector'],
                           computation_time['profile_vector'],
                           computation_time['search'],
                           computation_time['retrieval'],
                           computation_time['key_reconstruction'],
                           computation_time['decryption'],
                           ]
        processing_time_str = [formatter.format(computation_time['feature_vector']),
                               formatter.format(computation_time['profile_vector']),
                               formatter.format(computation_time['search']),
                               formatter.format(computation_time['retrieval']),
                               formatter.format(computation_time['key_reconstruction']),
                               formatter.format(computation_time['decryption']),
                               ]
        df = pd.DataFrame({"Processing time (sec)": processing_time,
                           "Computation steps": sub_modules})
        sns.barplot(x='Computation steps', y="Processing time (sec)", data=df)
        # ax.bar(sub_modules, processing_time_str)
        # ax.set_ylabel('Processing time (sec)', fontsize=12)
        # ax.set_xlabel('Computation steps', fontsize=12)
        ax.set_title('The total time: ' + formatter.format(total_time) + ' sec')

        plt.savefig('plot/search.png', dpi=200, format='png', bbox_inches='tight')
        # plt.show()
        plt.clf()

    def draw_image_upload_total_cost(self, hashtable_num, computation_time):
        computation_time = [2.5, 3, 2, 1.9, 2.8]
        hashtable_num = [40, 60, 80, 100, 120]
        # fig = plt.figure(figsize=(7, 5))
        plt.plot(computation_time, hashtable_num, color='red', marker='o',
                 linestyle='solid', linewidth=2, markersize=12)
        plt.xlabel('Image Uploading Time')
        plt.ylabel('Number of Hashtable(L)')

        plt.savefig('processing_time_imageupload.png', dpi=200, format='png', bbox_inches='tight')
        # plt.show()

    def draw_search_accuracy(self):
        x_dataset_size1 = [25, 50, 75, 100]
        y_accuracy1 = [.53, .55, .49, .43]

        x_dataset_size2 = [25, 50, 75, 100]
        y_accuracy2 = [.60, .52, .42, .37]
        # plt.xlim([0, 100])
        plt.ylim([0, 1])
        # fig = plt.figure(figsize=(7, 5))
        plt.plot(x_dataset_size1, y_accuracy1, color='red', marker='o',
                 linestyle='solid', linewidth=2, markersize=12)

        plt.plot(x_dataset_size2, y_accuracy2, color='blue', marker='*',
                 linestyle='solid', linewidth=2, markersize=12)

        plt.legend(["k=16, L=80", "k=32, L=120"])
        plt.ylabel('Searching and Retrieval Accuracy (%)')
        plt.xlabel('Search Dataset Size')

        plt.savefig('plot/search_accuracy.png', dpi=200, format='png', bbox_inches='tight')
        # plt.show()
def __main():
    plotting = EvaluationPlot()
    plotting.draw_search_accuracy()

if __name__ == '__main__':
    __main()