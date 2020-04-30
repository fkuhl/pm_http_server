import tornado.web


class FileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.enmdswith('/'):
            url_path += 'index.html'
        return url_path

    def get(self):
        # Serve app here when available
        self.render('./index.html')
