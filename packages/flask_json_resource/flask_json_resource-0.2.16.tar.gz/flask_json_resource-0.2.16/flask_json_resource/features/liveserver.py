import time
import threading


class LiveServer(object):
    """
    Represents a liveserver in a separate process.

    After starting, the server has three properties:
    * app
    * url
    * thread
    * port
    * server_name
    """

    def __init__(self, app):
        self.app = app

    def start(self, host='localhost', port=5555):
        """
        Start live server, setting thread and URL on self.

        Source: https://github.com/jerrykan/wsgi-liveserver/blob/master/wsgi_liveserver.py
        """
        def start(app, port, host):
            app.run(host=host, port=port, threaded=True, debug=True, use_reloader=False)

        # Create URL
        server_name = '{0}:{1}'.format(host, port)
        url = 'http://{0}'.format(server_name)

        # Set server name
        self.app.config.update({
            'SERVER_NAME': server_name
        })

        # Start the test server in the background
        thread = threading.Thread(target=start, args=[self.app, port, host])
        thread.start()

        self.thread = thread
        self.url = url
        self.port = port
        self.server_name = server_name

        time.sleep(1)

    def stop(self):
        """ Stop live server, joining thread until terminated. """
        self.thread._Thread__stop()
        self.thread.join()
