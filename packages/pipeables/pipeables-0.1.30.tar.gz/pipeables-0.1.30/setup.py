from setuptools import setup

setup(name='pipeables',
      version='0.1.30',
      description='Simiple queries and piping between different data sources',
      url='https://bitbucket.org/tdoran/pipeables/branch/v2package',
      author='Tony Doran',
      author_email='tdoran@atlassian.com',
      license='MIT',
      packages=['pipeables'],
      entry_points = {
        'console_scripts': [
          'pipeable=pipeables.command_line:pipeable',
          'makeList=pipeables.command_line:makeList',
          'makeValueList=pipeables.command_line:makeValueList',
          'intersection=pipeables.command_line:intersection'
        ]
      },
      install_requires=[
        'gdata',
        'pygresql'
      ],
      zip_safe=False)
