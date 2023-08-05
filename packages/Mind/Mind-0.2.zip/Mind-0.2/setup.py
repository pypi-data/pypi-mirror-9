from distutils.core import setup

setup(name='Mind',
      version='0.2',
      author='Jakov Manjkas',
      author_email='jakov.manjkas@gmail.com',
      url='https://github.com/Knowlege/Mind',
      description='Mind is library for games in Python',
      keywords ='pygame game tiled tiledtmxloader',
      long_description="""\
Mind is divided on three parts (for now): Mind.Knowledge, Mind.Orientation and Mind.Imagination(and Mind.Test but it's only for testing)\n
Next version will be 0.2.1\n
In that version tutorial will be added (probably)
For help see Documentation, Tutorial, use Mind.Tets file (and try to understand its code) and see pro_1.py and pro_2.py files (on GitHub).
""",
      packages = ['Mind'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Intended Audience :: Developers',
          'Topic :: Games/Entertainment'
          ]
)
