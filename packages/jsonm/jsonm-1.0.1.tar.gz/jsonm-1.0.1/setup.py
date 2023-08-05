from setuptools import setup, find_packages
setup(
    name="jsonm",
    version="1.0.1",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=[],
    scripts=[],
    url="https://github.com/dantezhu/jsonm",
    license="MIT",
    author="dantezhu",
    author_email="dantezhu@qq.com",
    description="pyhon object to (json + redis)",
)
