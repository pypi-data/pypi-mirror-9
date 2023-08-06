import crispy_forms

from setuptools import setup, find_packages

setup(
    name='django-crispy-forms-ng',
    version=crispy_forms.__version__,
    description='Best way to have Django DRY forms of the next generation.',
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=['forms', 'django', 'crispy', 'DRY'],
    author='Tzu-ping Chung and Miguel Araujo',
    author_email='uranusjr@gmail.com',
    url='http://github.com/maraujop/django-crispy-forms',
    license='MIT',
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
    zip_safe=False,
)
