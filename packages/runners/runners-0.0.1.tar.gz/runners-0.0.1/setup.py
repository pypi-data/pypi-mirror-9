import setuptools
import sys


REQUIREMENTS = [
    "kazoo==2.0",
]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "requirements":
        for req in REQUIREMENTS:
            print req
        sys.exit(0)

    setuptools.setup(
        name="runners",
        version="0.0.1",
        author="EDITD",
        author_email="engineering@editd.com",
        packages=setuptools.find_packages(),
        scripts=[],
        url="https://github.com/EDITD/runners",
        license="LICENSE.txt",
        description="Help with running stuff",
        long_description="View the github page (https://github.com/EDITD/runners) for more details.",
        install_requires=REQUIREMENTS
    )
