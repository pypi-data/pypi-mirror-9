from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

version = __import__('ecl_tools').get_version()

setup(name='django-ecl-tools',
      version=version,
      packages=find_packages(),
      author='Edge Case Labs, LLC',
      author_email='software@edgecaselabs.com',
      url='http://EdgeCaseLabs.com',
      install_requires={'django', 'boto', 'requests', 'celery'},
      description="EdgeCaseLabs' Django Tools",
      long_description=long_description,
      license='YMMV',
      data_files=[('README.rst', ['README.rst']),],
)


