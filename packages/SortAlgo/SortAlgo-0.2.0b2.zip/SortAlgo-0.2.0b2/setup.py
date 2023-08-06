from distutils.core import setup

setup(name = 'SortAlgo',
		version = '0.2.0b2',
		description = 'Some types of sorting Algorithm',
		author = 'Hiro Zhu',
		author_email = 'dingzezhu@gmail.com',
		#package_dir = {'SortAlgo':'lib'},
		packages = ['SortAlgo'],
		package_data = {'SortAlgo': ['readme/*.txt']},
		py_modules = ['TestFunc', ],
		scripts=['bin/sort.py',],
		#if you have c functions
		#ext_package='pkg',
        #ext_modules=[Extension('foo', ['foo.c'],
		#			library_dirs=['/usr/X11R6/lib'],
        #  			libraries=['X11', 'Xt']),
        #           Extension('subpkg.bar', ['bar.c'])],
		#data_files=[('bin',['sort.py'])]
		classifiers = [
			'Development Status :: 4 - Beta',
			'Topic :: Software Development :: Libraries',
		],
		long_description = 'Bucket Sorting, Insert Sorting',
		)

