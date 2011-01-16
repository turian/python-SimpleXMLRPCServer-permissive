from SimpleXMLRPCServer import SimpleXMLRPCServer

import sanitizexml

class PermissiveSimpleXMLRPCServer(SimpleXMLRPCServer):

    def _marshaled_dispatch(self, data, *args, **kwargs):
        data = sanitizexml.sanitize_xml(data,
            getattr(self, 'xml_warning_logger', None))
        return SimpleXMLRPCServer._marshaled_dispatch(self,
            data, *args, **kwargs)

def start_test_server(port):
    print 'Running permissive XML-RPC server on port %d' % port
    server = PermissiveSimpleXMLRPCServer(("localhost", port))
    def log(msg):
        print msg
    server.xml_warning_logger = log
    server.register_function(pow)
    server.register_function(lambda x,y: x+y, 'add')
    server.register_function(lambda s: s.upper(), 'upper')
    server.serve_forever()

if __name__ == '__main__':
    start_test_server(8000)
