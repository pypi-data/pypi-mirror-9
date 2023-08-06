from distutils.core import setup

setup(
    name='biflux',
    version='0.0.1',
    author='Lionel Montrieux',
    author_email='lionel@nii.ac.jp',
    url='https://github.com/lmontrieux/python-biflux',
    license='BSD',
    description='Python binding for BiFluX',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
    py_modules=['biflux'],
)
