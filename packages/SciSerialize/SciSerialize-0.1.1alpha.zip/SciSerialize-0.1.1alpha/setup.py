# -- encoding: utf-8 --

from setuptools import setup, find_packages

setup(name='SciSerialize',
      version='0.1.1alpha',
      description='Serialize scientific data to JSON or MessagePack.',
      author='Siegfried Guendert',
      author_email='siegfried.guendert@googlemail.com',
      url='https://github.com/SciSerialize/sciserialize-python',
      license='MIT',
      keywords='scientific serialize data exchange json msgpack',
      packages=find_packages(exclude=('docs',)),
      install_requires=['numpy', 'msgpack-python',
                        'python-dateutil', 'pandas'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ]
)
