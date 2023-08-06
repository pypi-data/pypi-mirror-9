from setuptools import setup

setup(
    name='django-gift-registry',
    version='0.4.2',
    description='A minimal wedding registry or gift registry app.',
    long_description=open('README').read(),
    url='https://gitlab.com/Sturm/django-gift-registry',

    author='Ben Sturmfels',
    author_email='ben@sturm.com.au',
    license='Apache License, Version 2.0',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

    keywords='wedding gift registry',

    packages=['gift_registry'],
    include_package_data=True,

    install_requires=[
        "Django >= 1.6",
        "PIL == 1.1.7",
    ],
)
