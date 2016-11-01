# put all files in this directory to the upper level as well as del the empty dirs

import os
import re
import shutil


def file_arrangement(abs_dir_path):
    """make dirs for every sort of file(diff suffix) in abs_dir_path"""
    if not os.path.isdir(abs_dir_path):
        return
    suffix_type = []
    sep = os.path.sep
    suffix_format = re.compile('(.*)\.(.*)') # name in group(1) and suffix in group(2)
    # using to split extension also can use os.path.splitext(path)
    for root, dirs, files in os.walk(abs_dir_path):
        dir_name = os.path.basename(root) # current directory name
        for file_name in files:
            curr_path = root + sep + file_name
            mapping = suffix_format.search(file_name)
            if mapping is None:
                new_path_name = abs_dir_path + sep + dir_name + '_' + file_name
                shutil.copy(curr_path, new_path_name)
                continue
            name = mapping.group(1)
            suffix = mapping.group(2)
            if suffix not in suffix_type:
                suffix_type.append(suffix)
                os.makedirs(abs_dir_path + sep + suffix)
            new_path_name = abs_dir_path + sep + suffix + sep + dir_name + '_' + file_name
            # that is put in to abs_dir_path\suffix\dir_name_filename
            shutil.copy(curr_path, new_path_name)


if __name__ == '__main__':
    path = input('''type an abs path or a rel path of a directory name
** must be a directory **
eg. \'C:\\a_dir\' or \'.\\another_dir\'
"q" to exit:''')
    if path == 'q':
        exit()
    if os.path.isabs(path):
        file_arrangement(path)
    else:
        file_arrangement(os.path.abspath(path))
    print('Done')
