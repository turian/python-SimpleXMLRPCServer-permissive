from SimpleXMLRPCServer import SimpleXMLRPCServer

class PermissiveSimpleXMLRPCServer(SimpleXMLRPCServer):
    pass

if __name__ == '__main__':
    print 'Running permissive XML-RPC server on port 8000'
    server = PermissiveSimpleXMLRPCServer(("localhost", 8000))
    server.register_function(pow)
    server.register_function(lambda x,y: x+y, 'add')
    server.serve_forever()
