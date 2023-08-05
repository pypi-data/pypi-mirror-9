from cStringIO import StringIO
import tarfile

def make_archive(path):
    stream = StringIO()
    try:
        tar = tarfile.open(mode='w', fileobj=stream)
        tar.add(path, arcname='.')
        return stream.getvalue()
    finally:
        stream.close()

