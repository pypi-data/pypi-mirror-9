from distutils.core import setup

setup(
    name='sba',
    version='1.6.4',
    author='Dennis Evangelista',
    author_email='devangel77b@gmail.com',
    packages=['sba',"sba.test"],
    scripts=['bin/eucsbademo.py'],
    description="wrapper for Lourakis' sparse bundle adjustment C library",
    keywords='SBA, sparse bundle adjustment, calibration, camera, camera calibration, photogrammetry',
    url='https://bitbucket.org/devangel77b/python-sba',
    license='GNU GPLv3',
    include_package_data=True,
    requires=[
        #"quaternions (>=0.0)" no longer required
        "numpy (>=1.6.1)"
    ],
    long_description=file('README.txt','r').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research'
        ],
)
