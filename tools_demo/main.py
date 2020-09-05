'''
quick start : python3 main.py --ip {dtp_server ip} --server_name dtp_server --client_name dtp_client --network traces_1.txt
'''
import os, platform
import time
import numpy as np
import argparse
from qoe import cal_single_block_qoe

# the numbers that you can control
numbers = 60
server_ip = "127.0.0.1"
port = "5555"

# define parser
parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, required=True, help="the ip of container_server_name that required")

parser.add_argument('--port', type=str, default="5555",help="the port of dtp_server that required,default is 5555, and you can randomly choose")

parser.add_argument('--numbers', type=int, default=60, help="the numbers of blocks that you can control")

parser.add_argument('--server_name', type=str, default="dtp_server", help="the container_server_name ")

parser.add_argument('--client_name', type=str, default="dtp_client", help="the container_client_name ")

parser.add_argument('--network', type=str, default=None, help="the network trace file ")

parser.add_argument('--block', type=str, default=None, help="the block trace file ")

parser.add_argument('--run_path', type=str, default="/home/aitrans-server/", help="the path of aitrans_server")

parser.add_argument('--solution_files', type=str, default=None, help="the path of solution files")

# parse argument
params                = parser.parse_args()
server_ip             = params.ip
port                  = params.port
numbers               = params.numbers
container_server_name = params.server_name
container_client_name = params.client_name
network_trace         = params.network
block_trace           = params.block
docker_run_path       = params.run_path
solution_files        = params.solution_files

# judge system
order_preffix = " " if "windows" in platform.system().lower() else "sudo "
tc_preffix = "" if network_trace else "# "

# move shell scripts to tmp directory
tmp_shell_preffix = "./tmp"
if not os.path.exists(tmp_shell_preffix):
    os.mkdir(tmp_shell_preffix)

# move logs to log diectory
logs_preffix = "./logs"
if not os.path.exists(logs_preffix):
    os.mkdir(logs_preffix)

# init trace
if block_trace:
    os.system(order_preffix + "docker cp " + block_trace + ' ' + container_server_name + ":%strace/block_trace/aitrans_block.txt" % (docker_run_path))
if network_trace:
    os.system(order_preffix + "docker cp " + network_trace + ' ' + container_server_name + ":%strace/traces.txt" % (docker_run_path))
    os.system(order_preffix + "docker cp " + network_trace + ' ' + container_client_name + ":%strace/traces.txt" % (docker_run_path))
if solution_files:
    os.system(order_preffix + "docker cp " + solution_files + ' ' + container_server_name + ":%sdemo/." % (docker_run_path))

# prepare shell code
client_run = '''
#!/bin/bash
cd {0}
{3} python3 traffic_control.py -load trace/traces.txt > tc.log 2>&1 &
./client --no-verify http://{1}:{2}
{3} python3 traffic_control.py --reset eth0
'''.format(docker_run_path, server_ip, port, tc_preffix)

server_run = '''
#!/bin/bash
cd {2}demo
g++ -shared -fPIC solution.cxx -I include -o libsolution.so > compile.log 2>&1
cp libsolution.so ../lib

cd {2}
{3} python3 traffic_control.py -aft 1 -load trace/traces.txt > tc.log 2>&1 &
LD_LIBRARY_PATH=./lib ./bin/server {0} {1} trace/block_trace/aitrans_block.txt &> ./log/server_aitrans.log &
'''.format(server_ip, port, docker_run_path, tc_preffix)

with open(tmp_shell_preffix + "/server_run.sh", "w", newline='\n')  as f:
    f.write(server_run)

with open(tmp_shell_preffix + "/client_run.sh", "w", newline='\n') as f:
    f.write(client_run)

# run shell order
order_list = [
    # "chmod +x %s/server_run.sh" %(tmp_shell_preffix),
    # "chmod +x %s/client_run.sh" %(tmp_shell_preffix),
    order_preffix + " docker cp ./traffic_control.py " + container_server_name + ":" + docker_run_path,
    order_preffix + " docker cp ./traffic_control.py " + container_client_name + ":" + docker_run_path,
    order_preffix + " docker cp %s/server_run.sh " %(tmp_shell_preffix) + container_server_name + ":" + docker_run_path,
    order_preffix + " docker cp %s/client_run.sh " %(tmp_shell_preffix) + container_client_name + ":" + docker_run_path,
    order_preffix + " docker exec -itd " + container_server_name + " nohup /bin/bash %sserver_run.sh" % (docker_run_path)
]

# os.system("sudo docker cp ./compile_run.sh " + container_server_name + ":" + docker_run_path)
for idx, order in enumerate(order_list):
    print(idx, " ", order)
    os.system(order)

time.sleep(1)
print("run client")
os.system(order_preffix + " docker exec -it " + container_client_name + "  /bin/bash %sclient_run.sh" % (docker_run_path))
time.sleep(1)
os.system(order_preffix + " docker cp " + container_client_name + ":%sclient.log ." % (docker_run_path))

stop_server = '''
#!/bin/bash
cd {0}
kill `lsof -i:{1} | awk '/server/ {{print$2}}'`
{2} kill `ps -ef | grep python | awk '/traffic_control/ {{print $2}}'`
{2} python3 traffic_control.py --reset eth0
'''.format(docker_run_path, port, tc_preffix)

with open(tmp_shell_preffix + "/stop_server.sh", "w", newline='\n')  as f:
    f.write(stop_server)

print("stop server")
# os.system("chmod +x %s/stop_server.sh" %(tmp_shell_preffix))
os.system(order_preffix + " docker cp %s/stop_server.sh " %(tmp_shell_preffix) + container_server_name + ":%s" % (docker_run_path))
os.system(order_preffix + " docker exec -it " + container_server_name + "  /bin/bash %sstop_server.sh" % (docker_run_path))
# move logs
os.system(order_preffix + " docker cp " + container_client_name + ":%sclient.log %s/." % (docker_run_path, logs_preffix))
os.system(order_preffix + " docker cp " + container_client_name + ":%stc.log %s/client_tc.log" % (docker_run_path, logs_preffix))
os.system(order_preffix + " docker cp " + container_server_name + ":%slog/server_aitrans.log %s/." % (docker_run_path, logs_preffix))
os.system(order_preffix + " docker cp " + container_server_name + ":%stc.log %s/server_tc.log" % (docker_run_path, logs_preffix))
os.system(order_preffix + " docker cp " + container_server_name + ":%sdemo/compile.log %s/compile.log" % (docker_run_path, logs_preffix))

# cal qoe
print("qoe : ", cal_single_block_qoe("client.log", 0.9))