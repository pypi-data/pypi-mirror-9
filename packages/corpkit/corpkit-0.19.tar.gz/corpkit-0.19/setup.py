from setuptools import setup, find_packages


setup(name='corpkit',
      version='0.19',
      description='A toolkit for working with parsed corpora',
      url='http://github.com/interrogator/corpkit',
      author='Daniel McDonald',
      package_data={'corpkit': ['*.jar', 'corpkit/*.jar'],
                    'corpkit': ['*.sh', 'corpkit/*.sh'],
                    'corpkit': ['*.ipynb', 'corpkit/*.ipynb'],
                    'dictionaries': ['*.p', 'dictionaries/*.p']},
      author_email='mcdonaldd@unimelb.edu.au',
      license='MIT',
      packages=['corpkit', 'dictionaries'],
      install_requires=[
                        "matplotlib >= 1.4.3",
                        "nltk >= 3.0.0",
                       ],
      #extras_require = {
      #                  'dependencies':  ["ReportLab>=1.2", "RXP"],
      #                  'view': ["pandas>=0.15.2"],
      #                 }
      #entry_points = {
      #                'corpkit': [
      #                'rst2pdf = project_a.tools.pdfgen [PDF]',
      #                'rst2html = project_a.tools.htmlgen',
      #                           ],
      #                }
      zip_safe=False)

#beautifulsoup4>=4.3.2
#lxml>=3.4.2
#numpy>=1.9.2
#pandas>=0.15.2
