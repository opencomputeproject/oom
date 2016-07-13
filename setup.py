from setuptools import setup, find_packages
setup(
    name="oom",
    version="0.4",
    description="Open Optical Monitoring",
    url="https://github.com/ocpnetworking-wip/oom.git",
    author="Don Bollinger",
    author_email="don@thebollingers.org",
    license="MIT",
    packages=find_packages(),
    package_data={'oom': ['lib/*', 'module_data/*', 'addons/*']},
    zip_safe=False
)
