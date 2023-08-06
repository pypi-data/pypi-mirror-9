from distutils.core import setup

setup(name = 'synergy_odm',
      version = '0.5',
      description = 'Synergy Object-Document Mapper',
      author = 'Bohdan Mushkevych',
      author_email = 'mushkevych@gmail.com',
      url = 'https://github.com/mushkevych/synergy_odm',
      packages = ['odm'],
      long_description = '''Object Document Mapping for convenient python-to-json and json-to-python conversions''',
      license = 'Modified BSD License',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
      ],
      requires=[]
)