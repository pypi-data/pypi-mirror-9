try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pyramid_i18n_wrapper',
    version='1.2.2',
    packages=['pyramid_i18n_wrapper',],
    description='pyramid_i18n_wrapper provides i18n wrapper apis for convenience.',
    author='Evan Nook',
    author_email='evannook@pylabs.net',
    url='https://bitbucket.org/evannook/pyramid_i18n_wrapper',
    license='BSD',
    long_description=open('README.txt').read(),
    install_requires = ['pyramid>=1.5'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
    ]
)
