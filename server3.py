import json
import http.server
import socketserver
import cgi
from urllib.parse import urlparse, parse_qs, unquote
from os import path
PORT = 7700

mimedic = [
            ('.html', 'text/html'),
            ('.htm', 'text/html'),
            ('.js', 'application/javascript'),
            ('.css', 'text/css'),
            ('.json', 'application/json'),
            ('.png', 'image/png'),
            ('.jpg', 'image/jpeg'),
            ('.gif', 'image/gif'),
            ('.txt', 'text/plain'),
            ('.avi', 'video/x-msvideo'),
        ]

class HandleServer(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        sendReply = False
        querypath = urlparse(self.path)
        filepath, query = querypath.path, querypath.query
        
        if filepath.endswith('/'):
            filepath += 'standalone.html'#不依赖其他文件的独立网页
        filename, fileext = path.splitext(filepath)
        for e in mimedic:
            if e[0] == fileext:
                mimetype = e[1]
                sendReply = True
        if sendReply == True:
            try:
                with open(filepath[1:],'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type',mimetype)
                    self.end_headers()
                    self.wfile.write(content)
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        query = urlparse(self.path)
        returncode, msg = 0, "success"
        if query.path.strip("/") == urlparse("/recoder/").path.strip("/") :
            form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     "CONTENT_TYPE":self.headers['Content-Type'],
                     })
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(f'Client: {str(self.client_address)}\n'.encode('ascii'))
            self.wfile.write(f'User-agent: {self.headers["user-agent"]}\n'.encode('ascii'))
            self.wfile.write(f'Path: {self.path}\n'.encode('ascii'))
            self.wfile.write('Form data:\n'.encode('ascii'))
            filename = form['name'].value
            filevalue  = form['data'].value
            filesize = len(filevalue)#文件大小(字节)
            #print len(filevalue)
        #print (filename)
            with open(f'{filename}.mp4','ab+') as f:
                f.write(filevalue)
            return
        else:
            returncode, msg = 1000, "url path should be /parse" 
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        output = {"returncode": returncode, "message": msg}
        self.wfile.write(json.dumps(output).encode("utf-8"))

handler = HandleServer

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("server starting..", PORT)
    httpd.serve_forever()