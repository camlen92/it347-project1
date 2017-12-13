# server.py
 
import sys, socket, select, re, traceback

HOST = "" 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9020

CONNECTION_NAME = {}

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif re.match(args[0], self.value):
            self.fall = True
            return True
        else:
            return False
        
        
def username(sock):
    (CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "unknown")

def server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    CHAT_BUFFER = []
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
    print "Listening on port: " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                sockfd.send("Welcome to Cameron's Chat Room! Go ahead and start messaging...\r\n")
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        for case in switch(data):
                            if case("^help\r\n$"):
                                print "User typed %s" % data
                                sock.send(("Chat Server Help: "
                                           "\n'help<cr><lf>' receives a response of a list of the commands and their syntax."
                                           "\n'test: words<cr><lf>' receives a response of 'words<cr><lf>'"
                                           "\n'name: <chatname><cr><lf>' receives a response of 'OK<cr><lf>'"
                                           "\n'get<cr><lf>' receives a response of the entire contents of the chat buffer."
                                           "\n'guests<cr><lf>' receives a response of the all guests currently connected to server."
                                           "\n'push: <stuff><cr><lf>' receives a response of 'OK<cr><lf>' The result is that '<chatname>: <stuff>' is added as a new line to the chat buffer."
                                           "\n'getrange <startline> <endline><cr><lf>' receives a response of lines <startline> through <endline> from the chat buffer. getrange assumes a 0-based buffer. Your client should return lines <startline> <endline-1>"
                                           "\n'SOME UNRECOGNIZED COMMAND<cr><lf>' receives a response 'Error: unrecognized command: SOME UNRECOGNIZED COMMAND<cr><lf>'"
                                           "\n'adios<cr><lf>' will quit the current connection.\r\n"))
                                break
                            if case("^test:\s[^\r\n]+\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)
                                sock.send(data[6:])
                                break
                            if case("^name:\s[^\r\n]+\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)
                                CONNECTION_NAME[id(sock)] = data.replace('\r\n', '')[6:]
                                print CONNECTION_NAME[id(sock)]
                                print CONNECTION_NAME
                                sock.send("OK\r\n")
                                break
                            if case("^get\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)

                                #for line in CHAT_BUFFER:
                                #   if any(CONNECTION_NAME[(id(sock))] in line for CONNECTION_NAME[(id(sock))] in CHAT_BUFFER):
                                          
                                sock.send("\n".join(CHAT_BUFFER) + "\r\n")
                                break
                            if case("^push:\s[^\r\n]+\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)
                                CHAT_BUFFER.append("%s: %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data[6:].replace('\r\n', '')))
                                sock.send("OK\r\n")
                                break
                            if case("^getrange(\s\d+){2}\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)
                                (start, end) = re.findall("\d+", data)
                                sock.send("\n".join(CHAT_BUFFER[int(start): int(end) + 1]) + "\r\n" )
                                break
                            if case("^adios\r\n$"):
                                print "%s typed %s" % ((CONNECTION_NAME[id(sock)] if id(sock) in CONNECTION_NAME else "Unknown"), data)
                                if id(sock) in CONNECTION_NAME:
                                    del CONNECTION_NAME[id(sock)]
                                sock.close()
                                if sock in SOCKET_LIST:
                                    SOCKET_LIST.remove(sock)
                                sys.exit()
                                break
                            if case(): # default
                                print "got bad request"
                                print data
                                sock.send("Error: unrecognized command: %s" % data)
                    else:
                        # remove the socket that"s broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                # exception 
                except Exception, err:
                    print traceback.format_exc()
                    print "Unexpected error:", sys.exc_info()[0]
                    continue

    server_socket.close()

# broadcast chat messages to all connected clients
if __name__ == "__main__":
    sys.exit(server())
