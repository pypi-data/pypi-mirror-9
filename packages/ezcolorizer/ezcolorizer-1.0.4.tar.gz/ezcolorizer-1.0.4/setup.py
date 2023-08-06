from setuptools import setup, find_packages

setup(
    name = 'ezcolorizer',
    version = '1.0.4',
    description = 'Add color to strings in python, great for menus and printing output',
    author = 'The Portly Penguin',
    author_email = 'admin@theportlypenguin.net',
    url = 'https://github.com/the-portly-penguin/ezcolorizer',
    license = 'MIT',
    install_requires = '',
    classifiers = [
        'Environment :: Console',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
    ],
    keywords='color setuptools development administration script',
    packages = find_packages(),
    entry_points = """
    [console_scripts]
    colorize = colorizer:main
    """,
)
