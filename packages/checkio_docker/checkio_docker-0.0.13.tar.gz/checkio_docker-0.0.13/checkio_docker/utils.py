import shutil as _shutil
from tempfile import mkdtemp


class TemporaryDirectory(object):
    def __init__(self):
        self.working_path = mkdtemp()
        self._closed = False

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.working_path)

    def __enter__(self):
        return self.working_path

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def cleanup(self):
        if not self._closed:
            _shutil.rmtree(self.working_path)
            self._closed = True
