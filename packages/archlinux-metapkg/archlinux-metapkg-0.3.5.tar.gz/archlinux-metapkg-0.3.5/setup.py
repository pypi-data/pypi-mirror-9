from distutils.core import setup

setup(
	name = 'archlinux-metapkg',
	version = '0.3.5',
	description = 'Creates metapackages for Arch Linux.',
	author = 'Claire Charron',
	author_email = 'claire@undeterminant.net',
	packages = ['metapkg'],
	scripts = ['scripts/metapkg'],
	url = 'https://github.com/Undeterminant/archlinux-metapkg',
	license = 'CC0'
)
