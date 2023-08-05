import sys
import glob
import pkgutil
import os
import fnmatch
from setuptools import setup

def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

#csv_files = find_data_files('data/', '*.csv')
all_data_files = find_data_files('data/', '*.*')
#all_data_files = find_data_files('script/', '*.*')

setup(
    name='pyCMM',
    version='0.0.2',
    author='Jessada Thutkawkorapin',
    author_email='jessada.thutkawkorapin@gmail.com',
    packages=['pyCMM',
              'pyCMM.app',
#              'linkana.presentation',
#              'linkana.db',
              ],
#    scripts=['bin/linkana_gen_sa_db_chr6_bwa',
#             'bin/linkana_gen_sa_db_chr18_bwa',
#             'bin/linkana_gen_sa_db_chr19_bwa',
#             'bin/linkana_gen_sa_db_chr6_mosaik',
#             'bin/linkana_gen_sa_db_chr18_mosaik',
#             'bin/linkana_gen_sa_db_chr19_mosaik',
#             'bin/linkana_gen_sa_db_chr9_axeq',
#             'bin/linkana_export_xls_chr6_bwa',
#             'bin/linkana_export_xls_chr18_bwa',
#             'bin/linkana_export_xls_chr19_bwa',
#             'bin/linkana_export_xls_chr6_mosaik',
#             'bin/linkana_export_xls_chr18_mosaik',
#             'bin/linkana_export_xls_chr19_mosaik',
#             'bin/linkana_export_xls_chr9_axeq',
##             'script/wrapped_summarize_annovar',
#             ],
    package=['pyCMM'],
#    package_data={'': ['data/CBV/*.cbv']
#                  },
    data_files=all_data_files,
#    data_files=[('data/family0008_chr18/', ['data/family0008_chr18/*.csv',
#                                            ]),
#                ],
    url='http://pypi.python.org/pypi/pyCMM/',
    license='LICENSE.txt',
    description='further linkage analysis',
    long_description=open('README').read(),
#    install_requires=["pysam >= 0.7"],
)
