from setuptools import setup

setup (
    name='jinja2-commentif',
    version='0.1',
    description='Jinja2 extension to automatically add a comment prefix on each line',
    author='Laurent Coustet',
    author_email='ed@zehome.com',
    url='https://github.com/zehome/jinja2-commentif',
    license='BSD2',
    packages=['jinja2_commentif'],
    install_requires=[
        'Jinja2>=2.4',
        'Pygments>=1.5'
    ],
    classifiers=[
    ],
)
