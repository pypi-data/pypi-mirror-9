#Copyright (c) 2011-2012 Litle & Co.
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

import urllib2
import paramiko
import os
import time
import socket
import io
import ssl
import errno
from time import gmtime, strftime

class Communications:
    def __init__(self, Configuration):
        self.Timeout = Configuration.timeout
        self.Proxy = Configuration.proxy
        self.Url = Configuration.url
        
    def http_post(self, post_data, url=None, proxy=None, timeout=None):
        if (url != None):
            self.Url = url
        if (proxy != None):
            self.Proxy = proxy
        if (timeout != None):
            self.Timeout = timeout
            
        req = urllib2.Request(url= self.Url, data=post_data)
        req.add_header('Content-type', 'text/xml')
            
        try: 
            if (self.Proxy != None) :  
                proxy_handler = urllib2.ProxyHandler({'https': self.Proxy}) 
                opener = urllib2.build_opener(proxy_handler)
                response = opener.open(req, timeout = self.Timeout)
            else:
                response = urllib2.urlopen(req, timeout = self.Timeout)
        except Exception,e:
            raise Exception("Error with Https Request, Please Check Proxy and Url configuration",e)
        
        responseXml = response.read()
        return responseXml

    def sendRequestFileToSFTP(self, requestFile, config):
        if (config.printXml) :
            print "\n",strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Entered sendRequestFileToSFTP"
        username = config.sftpUsername
        password = config.sftpPassword
        hostname = config.batchHost
        transport = paramiko.Transport((hostname, 22))
        try:
            if (config.printXml) :
                print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Connecting with username ", username
            transport.connect(username=username, password=password)
        except SSHException, e:
            raise Exception("Exception connect to litle")
        sftp = paramiko.SFTPClient.from_transport(transport)
        remoteFileNameProgress = 'inbound/' + os.path.basename(requestFile) + '.prg'
        remoteFileNameComplete = 'inbound/' + os.path.basename(requestFile) + '.asc'
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Putting local file ", requestFile, " to remote file ", remoteFileNameProgress
        sftp.put(requestFile, remoteFileNameProgress)
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Renaming remote file ", remoteFileNameProgress, " to ", remoteFileNameComplete
        sftp.rename(remoteFileNameProgress,  remoteFileNameComplete)
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Closing connection"
        sftp.close()
        transport.close()
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Closed connection"

    def receiveResponseFileFromSFTP(self, requestFile, responseFile, config):
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Entered receiveResponseFileFromSFTP"
        username = config.sftpUsername
        password = config.sftpPassword
        hostname = config.batchHost
        transport = paramiko.Transport((hostname, 22))
        try:
            if (config.printXml) :
                print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Connecting with username ", username
            transport.connect(username=username, password=password)
        except SSHException, e:
            raise Exception("Exception connect to litle")
        sftp = paramiko.SFTPClient.from_transport(transport)
        timeout = config.sftpTimeout
        start = time.time()
        while (time.time()-start) * 1000 < timeout:
            if (config.printXml) :
                print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"...Waiting 45 seconds..."
            time.sleep(45)
            success = True
            remoteFileName = 'outbound/' + os.path.basename(requestFile) + '.asc'
            try:
                if (config.printXml) :
                    print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Attempting to GET file ", remoteFileName, " and copy it locally to ", responseFile
                sftp.get(remoteFileName, responseFile)
            except Exception, e:
                success = False
            if (config.printXml) :
                print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"SFTP GET Succeeded: ", success
            if success:
                if (config.printXml) :
                    print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Removing remote file: ", success
                sftp.remove(remoteFileName)
                break

        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Closing connection"        
        sftp.close()
        transport.close()
        if (config.printXml) :
            print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"Closed connection"

    def sendRequestFileToIBC(self, requestFile, responseFile, config):
        hostName = config.batchHost
        hostPort = int(config.batchPort)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(int(config.batchTcpTimeout))

        if config.batchUseSSL == 'true':
            s = ssl.wrap_socket(s)

        try:
            s.connect((hostName, hostPort))
        except:
            raise Exception("Exception connect to litle")

        request = io.open(requestFile, 'r')
        ch = request.read(1)
        while ch != '':
            s.send(ch)
            ch = request.read(1)
            if not ch:
                break

        request.close()

        buf = bytearray(2048)
        buf[:] = ''
        with open(responseFile,'w') as respFile:
            while True:
                try:
                    s.recv_into(buf, 2048)
                    if buf == '':
                        break
                    respFile.write(buf)
                    buf[:] = ''
                except socket.error as e:
                    if e.errno != errno.ECONNRESET:
                        raise Exception("Exception receiving response")
            respFile.close()
        s.close()




