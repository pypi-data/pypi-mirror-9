from setuptools import setup

setup(
    name='full_stat',
    version='0.1.1',
    packages=['full_stat', 'full_stat.gui', 'full_stat.stats', 'full_stat.stats.corr', 'full_stat.stats.mean',
              'full_stat.stats.misc', 'full_stat.tests', 'full_stat.io_data', 'full_stat.gui_pyside'],
    url='https://github.com/yarnaid/full_stat',
    license='GPL v3',
    author='yarnaid',
    author_email='yarnaid@gmail.com',
    description='',
    install_requires=[
          'PySide',
          'scipy',
          'numpy',
          'pandas'
      ],
    entry_points={
              'console_scripts': [
                  'full_stat = full_stat.main:main',
              ],
              'gui_scripts': [
            'full_stat = full_stat.main:main',
            ]
              }
)
