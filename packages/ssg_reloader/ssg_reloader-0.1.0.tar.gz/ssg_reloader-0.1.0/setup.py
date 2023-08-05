from distutils.core import setup

upstream = 'https://github.com/ingwinlu/ssg_reloader'

setup(
    name='ssg_reloader',
    description='simple webserver, injects js into html sites that reloads sites when source is changed',
    version='0.1.0',
    url=upstream,
    packages=['ssg_reloader'],
    package_data={
            '' : ['LICENSE','README.md']
    },
    scripts=['ssgreloader'],
    requires = [
        'beautifulsoup4',
        'Flask',
        'itsdangerous',
        'Jinja2',
        'MarkupSafe',
        'Werkzeug'
    ],
    license='GPLv3',
    long_description='For a longer description, please have a look at ' + upstream,
    author='winlu',
    author_email='derwinlu+ssgreloader@gmail.com',
)

