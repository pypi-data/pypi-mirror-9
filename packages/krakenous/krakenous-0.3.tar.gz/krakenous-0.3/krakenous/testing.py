import unittest
from krakenlib.dataset import DataSet
from krakenlib.prerolled import folder_tentacle, convert_single_feature_numpy, convert_multiple_features_numpy
import os.path
from os import makedirs
import numpy as np
import krakenlib.errors


dataset = DataSet('shelve', {'db_path': 'testshelve'})
#
# print(dataset.feature_names())
# print(dataset.multiple_features(('numpy_feature',)))

for data_rec in enumerate(dataset.yield_data_records(())):
    print(data_rec)

print(convert_single_feature_numpy(dataset, 'ext3'))
print(convert_multiple_features_numpy(dataset, ('ext3', 'numpy_feature')))