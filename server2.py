# coding=utf-8
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from os import curdir, sep
import cgi
import logging
import time
from base64 import b64decode
import socket   #for sockets
import MySQLdb
import urllib
import urlparse
from json import dumps

PORT_NUMBER = 80
RES_FILE_DIR = "."


class myHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if(self.path.find("userID=")>=0):
            #print self.path
            #f = open(curdir + sep + self.path, 'rb')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            query_para = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            self.wfile.write("{\"result\":" + self.checkDb(query_para["userID"][0]) + "}")
            #f.close()
            print(self.path)
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    '''if self.path == "/":
           self.path = "/version0.html"

        try:
            # 根据请求的文件扩展名，设置正确的mime类型
            sendReply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True

            if sendReply == True:
                # 读取相应的静态资源文件，并发送它
                f = open(curdir + sep + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)'''

    def do_POST(self):
        logging.warning(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        #file_name = self.get_data_string()
        #path_name = '%s/%s.log' % (RES_FILE_DIR, file_name)
        #fwrite = open(path_name, 'a')

        #fwrite.write("name=%s\n" % form.getvalue("name", ""))
        #fwrite.write("addr=%s\n" % form.getvalue("addr", ""))
        #fwrite.close()
        if((form.type =="application/json")and(str(form).find("imageData"))):
            data = str(form).split("imageData\":\"")[1].split("\" }")[-2]
            data = data.replace("data:image/bmp;base64,","")
            handle = open("test.png", 'wb')
            handle.write(b64decode(data))
            handle.close()
        else:
            poststr = ("#x#"+str(form).split("#x#")[1]).split("#end#")[0]+"#end#";
            self.socketcon(poststr);
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Thanks for you post")

    def get_data_string(self):
        now = time.time()
        clock_now = time.localtime(now)
        cur_time = list(clock_now)
        date_string = "%d-%d-%d-%d-%d-%d" % (cur_time[0],
                                             cur_time[1], cur_time[2], cur_time[3], cur_time[4], cur_time[5])
        return date_string
    def checkDb(self,id):
        con = MySQLdb.connect(
            host="127.0.0.1",
            port=3306,
            user='cage',
            passwd='1234',
            db='test_ajax',
            charset='utf8'
        )
        cursor = con.cursor()
        result = "[]"
        try:
            cursor.execute("select * from info where userID = "+str(id))
            resultlist = []
            if(cursor.rowcount>0):
                for one in cursor.fetchall():
                    resultlist.append({"userID":one[1],"time":one[2],"power":one[3]})
                result =dumps(resultlist)
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            con.close()
        return result

    def socketcon(self,str):
        try:
        # create an AF_INET, STREAM socket (TCP)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            return
        print 'Socket Created'
        s.connect(("211.67.18.14",8286))
        try:
           s.sendall(str)
        except socket.error:
            print 'failed'
            return
        print 'success'
        s.close()



try:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print 'Started httpserver on port ', PORT_NUMBER

    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()