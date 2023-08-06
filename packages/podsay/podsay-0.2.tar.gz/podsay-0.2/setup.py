from distutils.core import setup

setup(
	name='podsay',
	version='0.2',
	packages=['podsay',],
	scripts=['bin/podsay',],
	license='GNU Lesser General Public License',
	long_description=open('README').read(),
)
