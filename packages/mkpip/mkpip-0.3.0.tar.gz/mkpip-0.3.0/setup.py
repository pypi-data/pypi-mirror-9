import os
from setuptools import setup

# Starfinder
# Find observable objects in your night sky.

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mkpip",
    version = "0.3.0",
    description = "mkpip",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    license = "GPLv3+",
    keywords = "pip python package pypi",
    url = "https://bitbucket.org/johannestaas/mkpip",
    packages=['mkpip'],
    package_dir={'mkpip': 'mkpip'},
    long_description=read('README.md'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
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
        'Topic :: Utilities',
    ],
    install_requires=[
    ],
    entry_points = {
        'console_scripts': [
            'mkpip = mkpip.bin:mkpip',
            'bumpy = mkpip.bumpy:main',
            'mkmod = mkpip.mkmod:main',
        ],
    },
    package_data = {
        'mkpip': [
            'boilerplate/.gitignore', 
            'boilerplate/setup.pyt',
            'boilerplate/README.md',
            'boilerplate/MANIFEST.in',
            'boilerplate/LICENSE',
            'boilerplate/name/*'
        ],
    },
    include_package_data = True,
)
