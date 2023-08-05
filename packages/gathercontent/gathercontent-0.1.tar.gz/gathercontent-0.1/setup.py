from setuptools import setup

setup(name='gathercontent',
      version='0.1',
      description='A very simple API wrapper for Gather Content',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='gather content gathercontent',
      url='http://bitbucket.org/wearefarm/gathercontent',
      author='Jon Atkinson',
      author_email='jon@wearefarm.com',
      license='MIT',
      packages=['gathercontent'],
      install_requires=[
          'requests==2.5.1',
      ],
      include_package_data=True,
      zip_safe=False)
