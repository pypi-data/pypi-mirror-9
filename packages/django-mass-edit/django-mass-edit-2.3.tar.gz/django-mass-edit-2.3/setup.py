from setuptools import setup, find_packages

setup(
    name = "django-mass-edit",
    version = "2.3",
    author = "David Burke",
    author_email = "david@burkesoftware.com",
    description = ("Make bulk changes in the Django admin interface"),
    license = "BSD",
    keywords = "django admin",
    url = "https://github.com/burke-software/django-mass-edit",
    packages=find_packages(),
    include_package_data=True,
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=['django']
)
