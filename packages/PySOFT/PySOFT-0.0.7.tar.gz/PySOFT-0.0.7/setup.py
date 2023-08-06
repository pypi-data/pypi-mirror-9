from setuptools import setup


def readme():
	with open('README.rst') as f:
		return f.read()

setup(
	name='PySOFT',
	version='0.0.7',
	description='SOFT (Simple Omnibus Format in Text) file parser',
	long_description=readme(),
	url='https://github.com/kpj/PySOFT',
	author='kpj',
	author_email='kpjkpjkpjkpjkpjkpj@gmail.com',
	license='MIT',
	packages=['pysoft', 'pysoft.tests'],
	test_suite='nose.collector',
	tests_require=['nose'],
	scripts=['bin/pysoft'],
	install_requires=[]
)
