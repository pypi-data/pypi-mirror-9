#!/usr/bin/env python3
import argparse
import os
import sys
import ssl
import cgi
import os.path as path
import http.server as http

upload_page = '''
<form method="POST" enctype="multipart/form-data">
File to upload: <input type="file" name="upfile"><br>
<input type="submit" value="Send">
</form>
'''


class UploadHandler(http.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        self.wfile.write(upload_page.encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.end_headers()

        form = cgi.FieldStorage(
                    environ={
                        'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE': self.headers['content-type']},
                    fp=self.rfile,
                    headers=self.headers)

        for field in form.keys():
            item = form[field]
            name = path.join(os.getcwd(), item.filename)

            if path.exists(name):
                self.wfile.write('{} failed: already exists\n'.format(
                    item.filename).encode('utf-8'))
                continue
            with open(name, 'wb') as file:
                file.write(item.file.read())
                self.wfile.write('{} has been uploaded\n'.format(
                    item.filename).encode('utf-8'))


def check_cert(dir):
    """
    check_dir(path) -> bool
    Test whether dir constain a valid key/cert pair
    """
    try:
        for i in 'cert', 'key':
            open(path.join(dir, 'https-%s.pem' % i)).close()
    except (FileNotFoundError, PermissionError) as e:
        print('Could not use %s: %s. Using http only.' % (dir, e.args[1]))
        return False
    except Exception as e:
        print('Error %d: %s' % e.args)
        sys.exit(e.errno)
    return True


def serve(address, port, tls_dir, upload):
    """
    Starts serving on http[s]://address:port
    tls_dir (filepath): directory which contains the key/cert pair
    upload  (bool): turn on/off the upload only server mode
    """
    use_tls = check_cert(tls_dir)
    port = 80 if port == 443 and not use_tls else port
    bind = (address, port)

    try:
        if upload:
            server = http.HTTPServer(bind, UploadHandler)
        else:
            server = http.HTTPServer(bind, http.SimpleHTTPRequestHandler)
        if use_tls:
            try:
                protocol = ssl.PROTOCOL_TLSv1_2
            except AttributeError:
                print('hyp needs TLSv1.2. You must have openssl >= 1.0.1')
                sys.exit(1)
            tls_socket = ssl.wrap_socket(server.socket, server_side=True,
                    certfile=path.join(tls_dir, 'https-cert.pem'),
                    keyfile=path.join(tls_dir,'https-key.pem'),
                    ssl_version=protocol)
            server.socket = tls_socket
    except Exception as e:
        print('Error %d: %s' % e.args)
        sys.exit(e.errno)

    print('Serving on %s:%d...' % (address, port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(' Bye.')
        server.socket.close()


def main():
    parser = argparse.ArgumentParser(description='Hyperminimal https server')
    parser.add_argument('address', nargs='?',
                        type=str, default='0.0.0.0',
                        help='bind ip address (default: 0.0.0.0)')
    parser.add_argument('port', nargs='?',
                        type=int, default=443,
                        help='bind port number (default: 80 or 443)')
    parser.add_argument('-u', '--upload', action='store_true',
                        help='only accept and save file as POST requests')
    parser.add_argument('-t', '--tls',
                        type=str, dest='tls_dir', metavar='DIR',
                        default='/usr/local/etc/openssl',
                        help='cert/key pair directory. Must be PEM '
                        'formatted and named https-key.pem, https-cert.pem '
                        '(default: /usr/local/etc/openssl)')
    args = parser.parse_args()
    serve(**vars(args))
