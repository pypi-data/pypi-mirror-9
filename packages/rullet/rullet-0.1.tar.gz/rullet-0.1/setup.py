from setuptools import setup

setup(name='rullet',
      version='0.1',
      description='Just a script selecting an item from an array randomly',
      url='http://github.com/minsoopark/Rullet',
      author='Minsoo Park',
      author_email='minsoo1003@gmail.com',
      license='MIT',
      packages=['rullet'],
      zip_safe=False,
      entry_points = {
        'console_scripts': ['rullet=rullet.command_line:main'],
      })
