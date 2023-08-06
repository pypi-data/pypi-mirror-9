from __future__ import print_function

from setuptools import setup, find_packages


setup(name='zygomorphic',
      version='0.2.3',
      description='Zygomorphic!',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Topic :: Multimedia :: Graphics',
      ],
      keywords='bumpr test',
      url='https://github.com/storborg/zygomorphic',
      author='Scott Torborg',
      author_email='storborg@gmail.com',
      install_requires=[
          'six>=1.5.2',
      ],
      license='MIT',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
