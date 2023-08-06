try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst', 'r') as f:
    readme = f.read()

packages = [
    'buttercms',
    'buttercms.templates',
]

setup(name='buttercms-django',
        version='0.1',
        description='Company blogs as a service. Built for developers.',
        long_description=readme,
        url='https://www.buttercms.com',
        author='ButterCMS',
        author_email='jake@buttercms.com',
        license='MIT',
        packages=packages,
        install_requires=['requests'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Environment :: Web Environment',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Django',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
        ],
        keywords='django blog service',
        include_package_data=True,
        zip_safe=False)