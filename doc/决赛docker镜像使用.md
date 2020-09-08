# 决赛系统使用

## docker 使用步骤

- docker镜像下载

  > docker pull aitrans/aitrans2:latest

- 创建服务端

  > docker run --privileged -dit --name {server container name} aitrans/aitrans2:latest

- 创建客户端

  > docker run --privileged -dit --name {client container name} aitrans/aitrans2:latest

- 进入容器

  > 进入服务端：docker attach {container name}
  >
  
- 文件系统

  > 服务端与客户端具有相同的文件，但是选手在不同端应执行不同的操作
  >
  > 进入比赛系统目录 ：cd /home/aitrans-server
  >
  > 镜像提供了可以编译运行的代码，并置于demo 目录下，选手应在服务端将自己的代码与"demo/solution.cxx"进行替换，使用后面一键运行脚本后可自动上传。
  >
  > 选手应将自己训练所需要的数据集上传至服务端指定位置。
  >
  > 退出但不关闭容器：Ctrl+P+Q（如若系统不支持该快捷键，请参考后面退出-重启容器的方法）。
  > 无法正常使用上述命令，则键入：exit，退出容器，后在命令行中重启容器。
  > 
  > docker attach {server container name}

- 一键运行

  > 在选手替换完自己的代码以及上传数据集后，为了简化编译运行过程，我们提供了一件运行脚本，选手可以前往github下载[一键运行脚本](https://github.com/TOPbuaa/AitransSolution/tree/master), 并使用如下命令使用默认算法和数据进行快速启动，并得到QoE分数.
  >
  > python3 main.py --server_name {server container name} --client_name {client container name} 
  >
  > 其他参数：
  >
  > --solution_files {solution files} 上传本地算法，注意如果需要上传多个文件（包括.cxx、.hxx和模型文件等等），建议使用通配符进行匹配，如上传reno目录下的所有文件："./reno/."
  >
  > --network {network trace path} 上传本地网络trace；
  >
  > --block {block trace path} 上传本地block trace；
  >
  > --run_times {number of running times} 需要重复运行的次数

# Docker 常用命令总结

(未接触过docker的选手，可阅读入门教程：[菜鸟教程](https://www.runoob.com/docker/docker-tutorial.html))

- 查看本地已下载的镜像

  > docker images

- 查看本地所有已创建的容器状态

  > docker ps -a

- 启动容器

  > docker start {container name}

- 进入容器

  > docker attach {container name}

- 拷贝本地文件进入容器指定目录

  > docker cp {local source files path} {container name}:{destination path in docker}
  > 
  > 同理，拷贝容器文件到本地：docker cp {container name}:{source path in docker} {local destination files path} 


# 决赛系统进阶内容（非必须）

  本部分内容主要讲述一键运行脚本控制系统运转过程，帮助部分不想按[一键运行脚本](https://github.com/AItransCompetition/AitransSolution/tree/master/tools_demo)流程走的选手进行探索。

  ## 编译阶段

​	首先选手提交的是.cxx和.hxx文件，我们会将这些文件放置在容器目录：/home/aitrans-server/demo，进入该目录后，键入命令

	> g++ -shared -fPIC solution.cxx -I include -o libsolution.so

即可在当前路径下生成动态链接库“libsolution.so”，通过cp命令，将其拷贝至“/home/aitrans-server/lib”目录下，至此完成编译阶段。

在该阶段，选手运行编译命令可以看到自己算法语法报错的地方。

  ## 服务端启动

​	进入到目录“/home/aitrans-server”，这里面有2个可执行文件——server和client，对应的就是我们启动服务端和客户端所用到的脚本，在服务端键入命令：

	> LD_LIBRARY_PATH=./lib ./bin/server {server ip} {server port} trace/block_trace/aitrans_block.txt &> ./log/server_aitrans.log

​	即可启动服务端，注意替换服务端ip，port可以任意填写一个未被占用的端口，默认server发包所使用的block数据源自“/home/aitrans-server/trace/block_trace/aitrans_block.txt”，选手可以通过替换该文件内容或者替换该文件路径来实现指定block数据集。服务端所有的输出都会被重定向到文件“/home/aitrans-server/log/server_aitrans.log”中，包括solution.cxx中的printf输出（建议算法上传提交前要关闭，否则影响性能）。

  ## 客户端启动

​	完成服务端启动后，我们可以进入客户端容器，并在相同的目录“/home/aitrans-server”中键入命令：

	> ./client --no-verify http://{server ip}:{server port}

​	即可启动客户端，注意替换服务端ip和port，等待服务端发完全部block后，客户端和服务端都会自动停止，所以请耐心等候。

​	至此完成了整个系统运行流程。

  ## TC（Traffic Control）限速

​	为了模拟出各种网络场景，我们使用了linux的tc命令，选手可以在服务端和客户端启动之前，键入命令：

	> python3 traffic_control.py -load {network trace path} > tc.log

​	即可在后台自动根据网络trace调整网络环境，因为理论上客户端和服务端应该同时做次操作，所以人工跑可能会有时间同步问题。

