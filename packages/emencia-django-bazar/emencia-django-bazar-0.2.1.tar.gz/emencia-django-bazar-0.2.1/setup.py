from setuptools import setup, find_packages

setup(
    name='emencia-django-bazar',
    version=__import__('bazar').__version__,
    description=__import__('bazar').__doc__,
    long_description=open('README.rst').read(),
    author='David Thenon',
    author_email='dthenon@emencia.com',
    url='https://github.com/emencia/emencia-django-bazar',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'autobreadcrumbs>=1.0',
        'django-braces>=1.2.0,<1.4',
        'crispy-forms-foundation>=0.5.0',
        'django-taggit==0.12.3',
        'django-taggit-templatetags2==1.4.0',
    ],
    include_package_data=True,
    zip_safe=False
)