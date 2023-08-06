from cStringIO import StringIO
import tarfile

import logging

root_logger = logging.getLogger()

def make_archive(path, logger=root_logger):
    stream = StringIO()
    try:
        tar = tarfile.open(mode='w', fileobj=stream)
        tar.add(path, arcname='.')
        logger.info(tar.getnames())
        return stream.getvalue()
    finally:
        stream.close()

