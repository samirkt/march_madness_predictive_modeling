from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    "bs4",
    "keras",
    "numpy",
    "pandas",
    "requests",
    "sklearn",
]

setup(
    name='mm_modeling',
    version='0.0.1',
    author='Samir Townsley',
    author_email='samirtownsley@gmail.com',
    description='Framework for developing March Madness predictive models',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/samirkt/march_madness_predictive_modeling',
    project_urls = {
        "Issues": "https://github.com/samirkt/march_madness_predictive_modeling/issues",
        "PRs": "https://github.com/samirkt/march_madness_predictive_modeling/pulls",
    },
    packages = find_packages(exclude=["test"]),
    install_requires=requirements,
)
