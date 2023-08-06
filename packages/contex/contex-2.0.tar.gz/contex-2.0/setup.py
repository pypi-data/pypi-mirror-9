from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='contex',
      version='2.0',
      description='Contextual string manipulation',
      long_description=readme(),
      url='https://notabug.org/Uglemat/Contex',
      author='Mattias Ugelvik',
      author_email='uglemat@gmail.com',
      license='GPL3+',
      packages=['contex'],
      classifiers=[
          "Topic :: Text Processing :: General",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2.7'
          
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      package_data={
          'readme': ['README.rst'],
      },
      include_package_data=True,
      zip_safe=False)
