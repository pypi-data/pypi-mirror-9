from setuptools import setup, find_packages


setup(
    name='consumerism',
    version='0.3.6',
    description='Expert360 Python SQS consumer library',
    author='Expert360',
    author_email='info@expert360.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='boto sqs consumer',
    url='https://github.com/expert360/consumerism',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'boto>=2.34.0',
    ],
)
