# remove all the files which has less than 1080 pixes in height
# or less than 1920 pixes in length

import os
from PIL import Image

CONST_limit_length = 1920
CONST_limit_height = 1080


def delete_low_resolving_pic(abs_dir_path):
    """remove all files which resolution is less than 1920*1080 """
    if not os.path.isdir(abs_dir_path):
        return
    pic_type = ['.jpg', '.png']
    sep = os.path.sep
    for each_file in os.listdir(abs_dir_path):
        name, extension = os.path.splitext(each_file)
        if extension not in pic_type:
            continue
        img_path = abs_dir_path + sep + each_file
        img = Image.open(img_path)
        length, weight = img.size
        if length < CONST_limit_length or weight < CONST_limit_height:
            del img
            os.remove(img_path)
            # print('removing ' + img_path)

if __name__ == '__main__':
    path = input("""
Usage: remove all file in a directory
please input a abs path or a rel path
eg. 'C\\a_dir' or '.\\another_dir'
'q' to exit':""")
    if path == 'q':
        exit()
    if os.path.isabs(path):
        delete_low_resolving_pic(path)
    else:
        delete_low_resolving_pic(os.path.abspath(path))
    print('Done')


