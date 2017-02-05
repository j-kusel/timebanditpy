import socket, sys, time

tbsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 7464


#try:
print tbsock.connect(('localhost', port))
#tbsock.listen(8)

#except socket.error as msg:
#    print 'bind fail: {0} {1}'.format(msg)
#    sys.exit()
n = 0
while True:
    try:
        time.sleep(1)
        tbsock.send('ready')
        print tbsock.recv(1024)
    except KeyboardInterrupt:
        tbsock.close()
        sys.exit()
    finally:
        n += 1
