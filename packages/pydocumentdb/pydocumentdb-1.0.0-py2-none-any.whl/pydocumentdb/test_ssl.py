import socket, ssl, pprint, sys
host = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# require a certificate from the server
ssl_sock = ssl.wrap_socket(s,
                           # http://curl.haxx.se/ca/cacert.pem
                           ca_certs="cacert.pem", 
                           cert_reqs=ssl.CERT_REQUIRED)

ssl_sock.connect((host, 443))

print repr(ssl_sock.getpeername())
print ssl_sock.cipher()
print pprint.pformat(ssl_sock.getpeercert())

# Set a simple HTTP request -- use httplib in actual code.
ssl_sock.write("""GET / HTTP/1.0\r
Host: """ + host + """\r\n\r\n""")

# Read a chunk of data.  Will not necessarily
# read all the data returned by the server.
data = ssl_sock.read()
print data

# note that closing the SSLSocket will also close the underlying socket
ssl_sock.close()