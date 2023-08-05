from setuptools import setup


setup(name='django-iipimage',
      version='1.0',
      description='Django app to provide integration with IIPImage server',
      url='https://github.com/kcl-ddh/django-iipimage',
      author='Jamie Norrish',
      author_email='jamie@artefact.org.nz',
      packages=['iipimage'],
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
)
