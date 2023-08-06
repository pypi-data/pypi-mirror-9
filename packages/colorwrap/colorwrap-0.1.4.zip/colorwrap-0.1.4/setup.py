from distutils.core import setup

setup(
  name = 'colorwrap',
  packages = ['colorwrap'],
  scripts = ['colorwrap.bat'],
  version = '0.1.4',
  description = 'Wraps a shell command to make unix/ansi escape codes work on Windows.',
  author = 'Konvexum',
  author_email = 'info@konvexum.se',
  url = 'https://github.com/konvexum/colorwrap',
  download_url = 'https://github.com/konvexum/colorwrap/tarball/0.1',
  keywords = ['color', 'ansi', 'shell', 'escape', 'colorama'],
  classifiers = [
      'Development Status :: 4 - Beta',
	  'Environment :: Console',
	  'Environment :: Win32 (MS Windows)',
	  'Intended Audience :: Developers',
	  'Intended Audience :: System Administrators',
      'License :: OSI Approved :: MIT License',
	  'Operating System :: Microsoft :: Windows',
      'Programming Language :: Python :: 3',
      'Topic :: Utilities',
  ],
)