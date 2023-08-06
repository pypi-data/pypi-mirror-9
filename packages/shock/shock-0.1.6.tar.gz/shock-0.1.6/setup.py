from setuptools import setup

setup(
    name="shock",
    version='0.1.6',
    zip_safe=False,
    platforms='any',
    packages=[],
    install_requires=['netkit'],
    scripts=['shock/bin/shock.py'],
    url="https://github.com/dantezhu/shock",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="tool for server load performance testing",
)
