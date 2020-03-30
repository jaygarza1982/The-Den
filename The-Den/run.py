import server
import sys


conf_contents = []
with open(sys.argv[1], 'r') as conf_file:
    conf_contents = conf_file.readlines()

ip = conf_contents[0]
print(ip)
port = conf_contents[1]
database = conf_contents[2]
logging = conf_contents[3] == 'True'


server = server.server(ip, logging, database)