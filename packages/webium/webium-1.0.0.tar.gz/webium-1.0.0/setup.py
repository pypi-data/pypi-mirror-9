from setuptools import setup

version = '1.0.0'

setup(
    name='webium',
    version=version,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    packages=[
        'webium',
    ],
    include_package_data=True,
    author='Wargaming.NET',
    author_email='i_khrol@wargaming.net',
    url='http://www.wargaming.net/',
    description='Webium is a Page Object pattern implementation library for Python '
                '(http://martinfowler.com/bliki/PageObject.html). '
                'It allows you to extend WebElement class to your custom controls '
                'like Link, Button and group them as pages.',
    install_requires=[
        'selenium==2.43',
        'nose==1.3.3',
        'waiting==1.2.0',
    ],
    entry_points={
        'nose.plugins': ['browser_closer = webium.plugins.browser_closer:BrowserCloserPlugin'],
    },
)
