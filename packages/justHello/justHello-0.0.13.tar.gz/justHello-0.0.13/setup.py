from setuptools import setup, find_packages
import sys

setup(name='justHello',
      version= "0.0.13",
      description='only print Hello World',
      long_description="""this tool is just sample of pathon packaging.""",
      author='Kenichi Masuda',
      author_email='masuken@gmail.com',
      url='https://github.com/masudaK/printHello',
      packages=find_packages(),
      py_modules=[
          # 上記のpackagesで収まるので、特に使わない
          'bin/command'
          ],
      zip_safe = (sys.version>="2.5"), #2.5の頃はディレクトリとしてegg作らないとまずかった？
      entry_points={
          'console_scripts': ['command = bin.command:main']
      },
      install_requires=open('requirements.txt').read().splitlines(),
      license='GNU Lesser General Public License v3 or later (LGPLv3+)',
      keywords='',
      platforms='Linux',
      classifiers=['Intended Audience :: System Administrators',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Natural Language :: Japanese',
                   'Programming Language :: Python :: 3.4'
                   ],
      )
