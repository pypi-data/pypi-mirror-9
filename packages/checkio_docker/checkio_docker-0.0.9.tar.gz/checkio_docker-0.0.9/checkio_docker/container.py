class Container(object):
    def __init__(self, container, connection):
        self._container = container
        self._connection = connection

    def start(self):
        self._connection.start(container=self._container)

    def stop(self):
        self._connection.stop(container=self._container, timeout=2)

    def remove(self):
        self._connection.remove_container(container=self._container)

    def logs(self, stream=False, logs=False):
        return self._connection.attach(container=self._container, stream=stream, logs=logs)