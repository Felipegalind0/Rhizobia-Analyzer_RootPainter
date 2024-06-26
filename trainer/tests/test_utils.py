"""
Utilities used in other tests


Copyright (C) 2023 Abraham George Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import shutil

# Add the parent directory to sys.path
parent_dir = os.path.abspath('../')
sys.path.insert(0, parent_dir)


from metrics import get_metrics_str, get_metric_csv_row

def log_metrics(metrics, fpath):
    if not os.path.isfile(fpath):
        # write headers if file didn't exist
        print('date_time,true_positives,false_positives,true_negatives,'
              'false_negatives,precision,recall,f1,defined,duration',
              file=open(fpath, 'w+'))
    with open(fpath, 'a+') as log_file:
            log_file.write(get_metric_csv_row(metrics))
            log_file.flush()



def get_acc(pred, true):
    import numpy as np

    if hasattr(pred, 'cpu'):
        pred = pred.cpu()
    if hasattr(true, 'cpu'):
        true = true.cpu()

 
    if hasattr(pred, 'numpy'):
        pred = pred.numpy()
    if hasattr(true, 'numpy'):
        true = true.numpy()

    assert np.min(pred) >= 0
    assert np.max(pred) <= 1

    assert np.min(true) >= 0
    assert np.max(true) <= 1

    output_bool = pred.reshape(-1) >= 0.5
    target_bool = true.reshape(-1) >= 0.5
    return (np.sum(output_bool == target_bool) / true.size)
 


def dl_dir_from_zip(url, output_path):
    """ download a zip from url and place contents in output_path """
    import urllib.request
    import zipfile
    import glob
    # if the directory does not exist, assume it needs downloading
    if not os.path.isdir(output_path):
        print('downloading', url)
        urllib.request.urlretrieve(url, 'temp.zip')
        with zipfile.ZipFile("temp.zip", "r") as zip_ref:
            zip_ref.extractall('temp_zip_output')

        # remove the junk osx metadata that was in the zip file
        junk_osx_dir = os.path.join('temp_zip_output', '__MACOSX')

        if os.path.isdir(junk_osx_dir):
            shutil.rmtree(junk_osx_dir)

        os.remove(os.path.join(os.getcwd(), 'temp.zip'))
        
        zip_dir = os.listdir(os.path.join('temp_zip_output'))[0]
        zip_path = os.path.join('temp_zip_output', zip_dir)
        shutil.move(zip_path, output_path)
        shutil.rmtree('temp_zip_output')
