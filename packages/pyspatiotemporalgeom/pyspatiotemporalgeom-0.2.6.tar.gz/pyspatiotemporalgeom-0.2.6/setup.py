from setuptools import setup

def readme():
      with open('README.rst') as f:
                return f.read()

setup(name='pyspatiotemporalgeom',
      version='0.2.6',
      description='Spatiotemporal geometry libray. Curently a pure python library, not explicitly focused on speed.',
      long_description=readme(),
      url='https://bitbucket.org/marmcke/pyspatiotemporalgeom',
      author='Mark McKenney',
      author_email='marmcke@siue.edu',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
      ],
      packages=['pyspatiotemporalgeom', 'pyspatiotemporalgeom.utilities', 'pyspatiotemporalgeom.examples'],
      include_package_data=True,
      zip_safe=False)
