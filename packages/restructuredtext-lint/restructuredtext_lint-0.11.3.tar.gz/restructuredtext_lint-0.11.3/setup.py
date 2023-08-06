from setuptools import setup, find_packages


setup(
    name='restructuredtext_lint',
    version='0.11.3',
    description='reStructuredText linter',
    long_description=open('README.rst').read(),
    keywords=[
        'restructuredtext',
        'restructured text',
        'rest',
        'rst',
        'lint'
    ],
    author='Todd Wolfson',
    author_email='todd@twolfson.com',
    url='https://github.com/twolfson/restructuredtext-lint',
    download_url='https://github.com/twolfson/restructuredtext-lint/archive/master.zip',
    entry_points={
        'console_scripts': [
            'restructuredtext-lint = restructuredtext_lint.cli:main',
            'rst-lint = restructuredtext_lint.cli:main'
        ]
    },
    packages=find_packages(),
    license='UNLICENSE',
    install_requires=open('requirements.txt').readlines(),
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Markup'
    ]
)
