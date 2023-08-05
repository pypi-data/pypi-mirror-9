from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')

version = '0.3.3'
long_description = open(README).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.captcha',
      version=version,
      description="ZTFY captcha package",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Zope3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='ZTFY Zope3 captcha package',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pillow',
          'z3c.form',
          'z3c.template',
          'zope.annotation',
          'zope.component',
          'zope.dublincore',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
          'ztfy.cache',
          'ztfy.jqueryui >= 0.7.0',
          'ztfy.skin >= 0.5.0',
          'ztfy.utils',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.captcha.myams = ztfy.captcha.skin.myams:library'
          ]
      })
