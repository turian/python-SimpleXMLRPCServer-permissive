from SimpleXMLRPCServer import SimpleXMLRPCServer

class PermissiveSimpleXMLRPCServer(SimpleXMLRPCServer):
    pass

if __name__ == '__main__':
    port = 8000
    print 'Running permissive XML-RPC server on port %d' % port
    server = PermissiveSimpleXMLRPCServer(("localhost", port))
    server.register_function(pow)
    server.register_function(lambda x,y: x+y, 'add')
    server.serve_forever()
