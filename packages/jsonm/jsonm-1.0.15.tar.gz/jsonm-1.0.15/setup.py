from setuptools import setup, find_packages
setup(
    name="jsonm",
    version="1.0.15",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[],
    scripts=[],
    url="https://github.com/dantezhu/jsonm",
    license="MIT",
    author="dantezhu",
    author_email="dantezhu@qq.com",
    description="python object to (json + redis)",
)
