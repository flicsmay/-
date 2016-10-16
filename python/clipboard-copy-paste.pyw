#! python3
# pyperclip包用法
#
# 以一个关键字保存剪切板上复制的东西
# 之后以关键字从程序中提取到剪切板上
# clipboard-copy-paste.pyw - save and loads pieces of test to the clipboard
# Usage : py.exe clipboard-copy-paste.pyw save <keyword> - Saves clipboard to keyword.
#         py.exe clipboard-copy-paste.pyw <keyword> - Loads keyword to clipboard
#         py.exe clipboard-copy-paste.pyw list - Loads all keyword to clipboard

import shelve
import pyperclip
import sys

mcbShelf = shelve.open('mcb')

if len(sys.argv) == 3 and sys.argv[1].lower() == 'save':
    mcbShelf[sys.argv[2]] = pyperclip.paste() #以第二个参数为键值
elif len(sys.argv) == 2:
    if sys.argv[1].lower() == 'list':
        pyperclip.copy(str(list(mcbShelf.keys())))
    elif sys.argv[1] in mcbShelf:
        pyperclip.copy(mcbShelf[sys.argv[1]])

mcbShelf.close()
