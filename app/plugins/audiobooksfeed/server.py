import os
from aiohttp import web

class FileServer:
    def __init__(self, root_dir):
        self.app = web.Application()
        self.root_dir = root_dir

        
        self.app.router.add_get('/xml/{filename}', self.display_xml)
        self.app.router.add_get('/{dirname}/{filename}', self.download_file)
        self.app.router.add_get('/favicon.ico', self.ignore_favicon)

    async def download_file(self, request):
        dirname = request.match_info['dirname']
        filename = request.match_info['filename']
        file_path = os.path.join(self.root_dir, f'{dirname}/{filename}')

        if os.path.exists(file_path):
            return web.FileResponse(file_path, headers={'Content-Type': 'audio/mpeg'})
        else:
            return web.Response(status=404)  # File not found

    async def display_xml(self, request):
        filename = request.match_info['filename']
        xml_path = os.path.join(self.root_dir, filename)

        if os.path.exists(xml_path):
            return web.FileResponse(xml_path, headers={'Content-Type': 'application/xml'})
        else:
            return web.Response(status=404)  # File not found

    async def ignore_favicon(self, request):
        return web.Response(status=204)

    def start(self, host, port):
        web.run_app(self.app, host=host, port=port)

