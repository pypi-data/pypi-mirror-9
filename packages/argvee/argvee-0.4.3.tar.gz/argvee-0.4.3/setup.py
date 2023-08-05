import os
from setuptools import setup

# argvee
# Easily parse command line argument by virtue of the functions defined in the module

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "argvee",
    version = "0.4.3",
    description = "Easily parse command line argument by virtue of the functions defined in the module",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    license = "GPLv3+",
    keywords = "python programming argv argument parsing",
    url = "https://bitbucket.org/johannestaas/argvee",
    packages=['argvee'],
    package_dir={'argvee': 'argvee'},
    #long_description=read('README.md'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
    ],
    #entry_points = {
    #    'console_scripts': [
    #        'argvee = argvee.bin:argvee',
    #    ],
    #},
    #package_data = {
        #'argvee': ['catalog/*.edb'],
    #},
    #include_package_data = True,
)
