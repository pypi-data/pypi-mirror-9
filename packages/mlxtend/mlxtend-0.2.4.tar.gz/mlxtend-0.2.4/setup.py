from distutils.core import setup

setup(name='mlxtend',
      version='0.2.4',
      description='Machine Learning Library Extensions',
      author='Sebastian Raschka',
      author_email='se.raschka@gmail.com',
      url='https://github.com/rasbt/mlxtend',
      packages=['mlxtend',
                'mlxtend.sklearn',
                'mlxtend.matplotlib',
                'mlxtend.classifier',
                'mlxtend.evaluate',
                'mlxtend.preprocessing',
                'mlxtend.math',
                'mlxtend.text',
                'mlxtend.file_io',
                'mlxtend.pandas',
                'mlxtend.data',
                ],
      data_files = [('', ['LICENSE']),
                    ('', ['README.md']),
                    ('', ['docs/CHANGELOG.txt']),
                   ],
      license='GPLv3',
      platforms='any',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
      ],
      long_description="""

A library of Python tools and extensions for data science.


Contact
=============

If you have any questions or comments about mlxtend, please feel free to contact me via
eMail: se.raschka@gmail.com
or Twitter: https://twitter.com/rasbt

This project is hosted at https://github.com/rasbt/mlxtend

""",
    )
