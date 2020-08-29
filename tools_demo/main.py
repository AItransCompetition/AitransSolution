'''
quick start : python3 main.py --ip {dtp_server ip} --server_name dtp_server --client_name dtp_client --network traces_1.txt
'''
import os
import time
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

parser.add_argument('--run_path', type=str, default="/home/aitrans-server/", help="the path of aitrans_server")

params                = parser.parse_args()
server_ip             = params.ip
port                  = params.port
numbers               = params.numbers
container_server_name = params.server_name
container_client_name = params.client_name
network_trace         = params.network
docker_run_path       = params.run_path

client_run = '''
#!/bin/bash
cd {0}
./client --no-verify http://{1}:{2}
'''.format(docker_run_path, server_ip, port)

'''
todo : specify block trace
'''
server_run = '''
#!/bin/bash
cd {3}demo
g++ -shared -fPIC solution.cxx -I include -o libsolution.so
cp libsolution.so ../lib

cd {3}
python3 traffic_control.py -load {2} &
LD_LIBRARY_PATH=./lib ./bin/server {0} {1} trace/block_trace/aitrans_block.txt &> ./log/server_aitrans.log &
'''.format(server_ip, port, network_trace, docker_run_path)

with open("server_run.sh", "w")  as f:
    f.write(server_run)

with open("client_run.sh", "w") as f:
    f.write(client_run)

order_list = [
    "chmod +x server_run.sh",
    "chmod +x client_run.sh",
    "sudo docker cp ./traffic_control.py " + container_server_name + ":" + docker_run_path,
    "sudo docker cp ./server_run.sh " + container_server_name + ":" + docker_run_path,
    "sudo docker cp ./client_run.sh " + container_client_name + ":" + docker_run_path,
    "sudo docker exec -it " + container_server_name + " nohup /bin/bash %sserver_run.sh" % (docker_run_path)
]

# os.system("sudo docker cp ./compile_run.sh " + container_server_name + ":" + docker_run_path)
for idx, order in enumerate(order_list):
    print(idx, " ", order)
    os.system(order)

time.sleep(1)
os.system("sudo docker exec -it " + container_client_name + "  /bin/bash %sclient_run.sh" % (docker_run_path))
time.sleep(5)
os.system("sudo docker cp " + container_client_name + ":%sclient.log ." % (docker_run_path))

stop_server = '''
#!/bin/bash
cd %s
kill `lsof -i:%s | awk '/server/ {print$2}'`
python3 traffic_control.py --reset eth0
''' % (docker_run_path, port)

with open("stop_server.sh", "w")  as f:
    f.write(stop_server)

print("stop server")
os.system("sudo docker cp ./stop_server.sh " + container_server_name + ":%s" % (docker_run_path))
os.system("sudo docker exec -it " + container_server_name + "  /bin/bash %sstop_server.sh" % (docker_run_path))
os.system("sudo docker cp " + container_client_name + ":%sclient.log ." % (docker_run_path))

sum = 0
with open('client.log', 'r') as f:
    
    print(f.readline())
