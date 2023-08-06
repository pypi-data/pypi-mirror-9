from setuptools import setup, find_packages

setup(
    name="buzz_agent",
    version='1.1.10',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    zip_safe=False,
    platforms='any',
    install_requires=['requests'],
    scripts=['buzz_agent/bin/run_buzz_agent.py'],
    url="https://github.com/dantezhu/buzz",
    license="MIT",
    author="dantezhu",
    author_email="dantezhu@qq.com",
    description="agent for buzz system",
)
