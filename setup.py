from setuptools import setup, find_packages
setup(
    name = "oom",
    version = "0.1",
    description = "Open Optical Monitoring",
    url = "https://github.com/ocpnetworking-wip/oom.git",
    author = "Don Bollinger",
    author_email = "don@thebollingers.org",
    license = "MIT",
    packages = find_packages(),
#     packages = ["oom"],
    zip_safe = False
)
