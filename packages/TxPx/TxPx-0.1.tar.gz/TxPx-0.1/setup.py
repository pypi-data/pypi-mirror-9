"""
TxPx
"""
from setuptools import setup


cfg = dict(name='TxPx',
      version='0.1',
      description='Robust process management and communication for Twisted',
      url='http://github.com/Brightmd/TxPx',
      author='Bright.md',
      author_email='support@bright.md',
      license='MIT',
      packages=['txpx', 'txpx/test'],
      # dependency_links=[],
      install_requires=[
        # library:
        "twisted",
        # testing:
        "coverage",
        "pyflakes",
        "mock",
      ],
      zip_safe=False)

setup(**cfg)
