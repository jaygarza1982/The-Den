import server
import sys
logging = len(sys.argv) > 3
server = server.server(sys.argv[1], logging)