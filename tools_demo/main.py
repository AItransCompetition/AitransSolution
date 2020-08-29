import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import argparse

# the numbers that you can control
numbers = 60
server_ip = "127.0.0.1"
port = "5555"

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, required=True, help="the ip of container_server_name that required")

parser.add_argument('--port', type=str, default="5555",help="the port of dtp_server that required,default is 5555, and you can randomly choose")

parser.add_argument('--numbers', type=int, default=60, help="the numbers of blocks that you can control")

parser.add_argument('--server_name', type=str, default="dtp_server", help="the container_server_name ")

parser.add_argument('--client_name', type=str, default="dtp_client", help="the container_client_name ")

parser.add_argument('--network', type=str, default="trace.txt", help="the network trace file ")

params                = parser.parse_args()
server_ip             = params.ip
port                  = params.port
numbers               = params.numbers
container_server_name = params.server_name
container_client_name = params.client_name
network_trace         = params.network

docker_run_path = "/aitrans-server/"

compile_run = '''
#!/bin/bash
cd /aitrans-server/demo
g++ -shared -fPIC solution.cxx -I include -o libsolution.so
cp libsolution.so ../lib
'''

client_run = '''
#!/bin/bash
./client --no-verify http://{0}:{1}
'''.format(server_ip, port)

'''
todo : specify block trace
'''
server_run = '''
#!/bin/bash
cd /aitrans-server
LD_LIBRARY_PATH=./lib ./bin/server {0} {1} trace/block_trace/aitrans_block.txt &> ./log/server_aitrans.log &
python3 traffic_control.py -load {2} &
'''.format(server_ip, port, network_trace)

with open("compile_run.sh", "w") as f:
    f.write(compile_run)

with open("server_run.sh", "w")  as f:
    f.write(server_run)

with open("client_run.sh", "w") as f:
    f.write(client_run)

os.system("sudo docker cp ./compile_run.sh " + container_server_name + ":" + docker_run_path)
os.system("sudo docker cp ./server_run.sh " + container_server_name + ":" + docker_run_path)
os.system("sudo docker cp ./client_run.sh " + container_client_name + ":" + docker_run_path)
os.system("sudo docker exec -itd " + container_server_name + "  /bin/bash %sserver_run.sh" % (docker_run_path))
os.system("sudo docker exec -it " + container_client_name + "  /bin/bash %sclient_run.sh" % (docker_run_path))
os.system("sudo docker cp " + container_client_name + ":%sclient.log ." % (docker_run_path))

stop_server = '''
#!/bin/bash
kill `lsof -i:{} | awk '/server/ {print$2}'`
'''.format(port)

with open("stop_server.sh", "w")  as f:
    f.write(stop_server)
os.system("sudo docker cp ./stop_server.sh " + container_server_name + ":%s" % (docker_run_path))
os.system("sudo docker exec -it " + container_server_name + "  /bin/bash %sstop_server.sh" % (docker_run_path))

sum = 0
with open('client.log', 'r') as f:
    f.seek(0)
    sum = int(os.popen('wc -l server.log').read().split()[0])
