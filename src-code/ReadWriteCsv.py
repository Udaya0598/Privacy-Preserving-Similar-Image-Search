import csv


class ReadWriteCsv:
    def __init__(self):
        print("This is an impty constructor")

    def read_row(self, file_name):
        with open(file_name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                line_count += 1
            print(f'Processed {line_count} lines.')
            csv_file.close()

    def write_header(self, file_name, fieldnames):
        with open(file_name, mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            # Close the file object
            csv_file.close()

    def write_row(self, file_name, fieldnames, row):
        with open(file_name, mode='a+') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(row)
            #Close the file object
            csv_file.close()
def __main():
    dump = ReadWriteCsv()
    image_upload_headers = ['key processing','feature vector',
                       'profile vector','indexing',
                       'image encryption', 'storage']

    dump.write_header('image_upload.csv', image_upload_headers)
    dump.write_row('image_upload.csv')
    dump.read_row('image_upload.csv')

    image_search_headers = ['feature vector', 'profile vector,'
                            'index search','record from CS',
                            'reconstructing key','image decryption']

    dump.write_header('image_search.csv', image_search_headers)
    dump.write_row('image_search.csv')
    dump.read_row('image_search.csv')

if __name__ == '__main__':
    __main()