from setuptools import setup

setup(name='Pygmie',
      version='1.4',
      description='Webinterface for working with PostgreSQL queries',
      url='https://bitbucket.org/sras/py-pg-query-maker',
      author='Sandeep.C.R',
      author_email='sandeepcr2@gmail.com',
      license='MIT',
      packages=['pygmie'],
      include_package_data=True,
      entry_points={'console_scripts': ['pygmie=pygmie.pygmie:main',],},
      install_requires=[
          'flask',
          'psycopg2',
          'sqlparse'
      ],
      zip_safe=False)
