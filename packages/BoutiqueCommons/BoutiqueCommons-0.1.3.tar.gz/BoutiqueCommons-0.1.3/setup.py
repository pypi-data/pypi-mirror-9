from setuptools import setup


setup(
  name='BoutiqueCommons',
  version='0.1.3',
  description='Boutique Commons',
  packages=['boutiquecommons', 'boutiquecommons.template'],
  include_package_data=True,
  zip_safe=False,
  author='Boutiqueforge',
  author_email='hello@boutiqueforge.com',
  install_requires=[
      'Flask==0.10.1',
      'Jinja2==2.7.3'
  ],
)
