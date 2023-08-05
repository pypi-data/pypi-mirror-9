import csv
import os
from pyFRET import FRET_data

def parse_csv(filepath, filelist):
    donor_data = []
    acceptor_data = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        with open(current_file) as csv_file:
            current_data = csv.reader(csv_file, delimiter=',')
            for row in current_data:
                donor_data.append(float(row[0]))
                acceptor_data.append(float(row[1]))
    print donor_data, acceptor_data
    FRET_data_obj = FRET_data(donor_data, acceptor_data)
    return FRET_data_obj
        


parse_csv("/media/TOSHIBA EXT", ["test.csv"])