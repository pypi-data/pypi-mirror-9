from setuptools import setup, find_packages
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = "0.1"

setup(name="PyBlox",
      version=version,
      description="A Python MVC web framework.",
      long_description="""A Python web framework that utilizes some popular web technologies Several models are included and comes complete with a ready-to-go web site and admin backoffice with authentication. Some of the technologies used are: SQLAlchemy, AngularJS, Bootstrap, Datatables and more. It is meant for high performance and utilizes Gevent.""",
      classifiers=["Environment :: Web Environment"],
      keywords="python sqlalchemy angularjs framework responsive bootstrap admin",
      author="Noel Morgan",
      author_email="noel@pyblox.org",
      url="http://www.pyblox.org",
      license="MIT",
      packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "Paste>=1.7.5.1",
          "PasteScript>=1.7.5"
      ],
      setup_requires=["PasteScript>=1.7.5"],
      entry_points="""
      [paste.paster_create_template]
      PyBlox = pyblox.tmplt:PyBloxTemplate
      """,
      )

