from distutils.core import setup

setup(
    name='pytsort',
    version='0.1.1',
    description='',
    long_description='Topological Sorting in Python',
    author='Marko Tasic',
    author_email='mtasic85@gmail.com',
    url='https://github.com/mtasic85/pytsort',
    py_modules=['tsort'],
    packages=[],
    license='MIT License',
    platforms=['Any'],
    data_files=[('', ['LICENSE'])],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3.2',
    ],
)
