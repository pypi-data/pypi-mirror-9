from setuptools import setup

setup(name='fotatest',
      version='0.02',
      description='UIE FOTA test app',
      url='',
      author='Mike Cole',
      author_email='',
      license='Private',
      packages=['fotatest'],
      install_requires=[
            'selenium',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['fotatest/bin/fotatest'],
    )
