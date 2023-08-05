__author__ = 'Corey Lin'

from setuptools import setup,find_packages

setup(name='compare_man_pages_from_two_folders',
      version='1.0.0.dev1',
      description='A tool used to compare man pages with same name from separate folders',
      url='http://github.com/storborg/compare_man_pages_from_two_folders',
      author='Corey Lin',
      author_email='514971757@qq.com',
      license='MIT',
      packages=find_packages(),
      scripts=['bin/CompareManPagesScript.py'],
      install_requires=['PyXB'],
      zip_safe=False,
      classifiers=['Programming Language :: Python :: 2.7'])

# packages=['compare_man_pages_from_two_folders','compare_man_pages_from_two_folders.man_page_PyXB','compare_man_pages_from_two_folders.man_page_PyXB.com','compare_man_pages_from_two_folders.man_page_PyXB.com.nokia','compare_man_pages_from_two_folders.man_page_PyXB.com.nokia.oss','compare_man_pages_from_two_folders.man_page_PyXB.com.nokia.oss.fm','bin']