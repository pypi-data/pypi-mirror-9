from setuptools import setup

setup(
	description = 'A library for identifying and directly reading input devices',
	author = 'Mike Lang',
	author_email = 'mikelang3000@gmail.com',
	py_modules = ['inputdev'],
	version = '0.0.1421587592',
	long_description = "A library for identifying and directly reading input devices\n\nThis can be used to implement global hotkeys, keyloggers, mouse tracking\n\nUses sysfs interface mounted at /sys to determine device capabilities.\nExpects input devices to be available under /dev/input/ and readable\n(which on most machines requires root or to be in group 'input')\n",
	name = 'inputdev',
)
