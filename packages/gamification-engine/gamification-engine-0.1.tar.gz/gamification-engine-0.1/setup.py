import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pytz',
    'dogpile.cache',
    'pyramid_dogpile_cache',
    'flask',
    'flask-admin',
    'pylibmc',
    'psycopg2',
    'pymemcache'
    ]

setup(name='gamification-engine',
      version='0.1',
      description='gamification-engin',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        ],
      author='Marcel Sander, Jens Janiuk',
      author_email='marcel@gamification-software.com',
      url='https://www.gamification-software.com',
      keywords='web wsgi bfg pylons pyramid gamification',
      packages=find_packages()+["quickstart_template",],
      include_package_data=True,
      zip_safe=False,
      test_suite='gengine',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = gengine:main
      [console_scripts]
      initialize_gengine_db = gengine.scripts.initializedb:main
      gengine_quickstart = gengine.scripts.quickstart:main
      """,
     )
    
