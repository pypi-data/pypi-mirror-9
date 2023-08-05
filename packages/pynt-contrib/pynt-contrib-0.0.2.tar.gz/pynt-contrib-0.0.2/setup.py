from setuptools import setup
#from pynt import contrib
setup(
    name="pynt-contrib",
    version= "0.0.2",
    author="Raghunandan Rao",
    author_email="r.raghunandan@gmail.com",
#    url= contrib.__contact__, 
    packages=["pynt.contrib"],
    license="MIT License",
    description="Common pynt tasks.",
    long_description=open("README.rst").read()+"\n"+open("CHANGES.rst").read(),
    install_requires = ['pynt>=0.8.1']
)
