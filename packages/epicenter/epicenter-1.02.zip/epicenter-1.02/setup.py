from distutils.core import setup
import io
import epicenter


# Read function was suggested by Jeff Knupp with
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/,
# though he seems not to have created this function himself.
def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(name='epicenter',
      version=epicenter.__version__,
      packages=['epicenter'],
      url='http://www.forio.com/epicenter',
      description=('Python Package for interacting with the Forio '
                   'Epicenter Platform'),
      long_description=long_description,
      author='Brian Piper',
      author_email='bpiper@forio.com',
      keywords=['Forio', 'Epicenter']
      )
