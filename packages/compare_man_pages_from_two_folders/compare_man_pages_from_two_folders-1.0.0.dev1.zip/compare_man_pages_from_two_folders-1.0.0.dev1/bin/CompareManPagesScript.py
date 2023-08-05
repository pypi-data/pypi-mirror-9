__author__ = 'Corey Lin'

from compare_man_pages_from_two_folders.CompareManPages import *

compare = CompareManPages("man_pages_compare_result.txt")
compare.compare_man_pages_from_two_folders(FOLDER_ONE_PATH, FOLDER_TWO_PATH)
