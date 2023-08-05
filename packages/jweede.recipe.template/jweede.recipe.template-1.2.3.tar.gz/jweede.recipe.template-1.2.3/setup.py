from setuptools import setup, find_packages

setup(
    name="jweede.recipe.template",
    version="1.2.3",
    author="Jon Wedaman",
    author_email="jweede@gmail.com",
    url="http://github.com/jweede/amplecode.recipe.template",
    description="Buildout recipe for making files out of Jinja2 templates",
    long_description=open("README.rst").read(),
    classifiers=(
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Pre-processors",
    ),
    keywords="zc.buildout recipe template Jinja2",
    license="BSD",
    packages=find_packages(),
    namespace_packages=("jweede", "jweede.recipe"),
    install_requires=("setuptools", "zc.recipe.egg", "Jinja2", "zope.dottedname"),
    zip_safe=True,
    entry_points="""
        [zc.buildout]
        default = jweede.recipe.template:Recipe
    """,
)
