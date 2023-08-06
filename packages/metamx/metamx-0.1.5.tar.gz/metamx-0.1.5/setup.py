from setuptools import setup 

setup(
  name='metamx',
  version='0.1.5',
  author='ops',
  author_email='ops@metamarkets.com',
  packages=['metamx'],
  package_data={'':['config.yaml']},
  include_package_data=True,
  url='https://github.com/metamx/operations',
  description='Metamx Operations API',
  install_requires=['boto','pyyaml'],
)
