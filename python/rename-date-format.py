#! python3
# 用来实践批量重命名的程序
# 使用到shutil模块
# rename-date-format.py - Renames file-names with American MM-DD-YYYY date format
# to European DD-MM-YYYY

import shutil   # to handle high level files operations
import os
import re

# datePattern : to catch days in American format
datePattern = re.compile(r"""^(.*?) # to skip the before parts of the name
((0|1)?\d)- # months which starts with 0 or 1
((0|1|2|3)?\d)- # days which starts with 0/1/2
((19|20)\d\d) # years - starts with 19XX 20XX
(.*?)$
""", re.VERBOSE)

for amerFilename in os.listdir('.'):
    mo = datePattern.search(amerFilename)

    if mo is None:
        continue
    beforePart = mo.group(1)
    monthPart = mo.group(2)
    dayPart = mo.group(4)
    yearPart = mo.group(6)
    afterPart = mo.group(8)

    euroFilename = beforePart + dayPart + '-' + monthPart + '-' + yearPart + afterPart

    absWorkingDir = os.path.abspath('.')
    amerFilename = os.path.join(absWorkingDir, amerFilename)
    euroFilename = os.path.join(absWorkingDir, euroFilename)

    print('Renaming "%s" to "%s"...' % (amerFilename, euroFilename))
    shutil.move(amerFilename, euroFilename)
    """ shutil.move(src, dst)
        Recursively move a file or directory (src) to another location (dst).
        If the destination is an existing directory, then src is moved inside that directory.
        If the destination already exists but is not a directory,it may be overwritten depending on os.rename() semantics.
        If the destination is on the current filesystem, then os.rename() is used. Otherwise, src is copied
        ** the third If statement is exactly what I done. **
        (using shutil.copy2()) to dst and then removed."""


