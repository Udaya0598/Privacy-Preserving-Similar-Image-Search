# https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python

import fileinput
import re


class AccuracyLogging:

    @staticmethod
    def read_value_by_key(key):
        value = None
        with open("accuracy_count.txt") as primary_id_file:
            for line in primary_id_file:
                name, val = line.partition("=")[::2]
                #print(name, val)
                if name == key:
                    value = val
        primary_id_file.close()
        return value

    @staticmethod
    def write_value_by_key(key, value):
        regex = re.compile(r"^.*"+key+"=.*$", re.IGNORECASE)
        for line in fileinput.input("accuracy_count.txt", inplace=True):
            line = regex.sub(key+"=%s" % str(value), line)
            print('{}'.format(line), end='')  # for Python 3

