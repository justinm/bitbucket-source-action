from glob import glob

import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="bitbucket_source_action",
    version="0.0.1",

    description="An AWS CDK Construct for sourcing repositories from on-prem BitBucket instances.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Justin McCormick <me@justinmccormick.com>",

    packages=['bitbucket_actions'],

    package_dir={
        'bitbucket_actions': 'bitbucket_actions',
    },

    package_data={
        'bitbucket_actions': ['function/*']
    },

    install_requires=[
        "aws-cdk.core>=1.76.0",
        "aws-cdk.aws-apigatewayv2>=1.76.0",
        "aws-cdk.aws-apigatewayv2-integrations>=1.76.0",
        "aws-cdk.aws-lambda-python>=1.76.0"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
