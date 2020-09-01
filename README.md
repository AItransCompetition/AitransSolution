# AitransSolution
Solution demo for Aitrans players

## Building
```bash
$ cd src/aitrans
$ g++ -c solution.cxx -I include
```

# 决赛系统使用

## docker 使用步骤

- docker镜像下载

  > docker pull aitrans/aitrans2:latest

- 创建服务端

  > docker run --privileged -dit --name {server container name} aitrans/aitrans2:latest

- 创建客户端

  > docker run --privileged -dit --name {client container name} aitrans/aitrans2:latest

- 查看服务端信息

  > 进入服务端：docker attach {container name}
  >
  > 查看服务端的ip：ifconfig eth0 | grep inet

- 文件系统

  > 服务端与客户端具有相同的文件，但是选手在不同端应执行不同的操作
  >
  > 进入比赛系统目录 ：cd /home/aitrans-server
  >
  > 镜像提供了可以编译运行的代码，并置于demo 目录下，选手应在服务端将自己的代码与"demo/solution.cxx"进行替换。
  >
  > 选手应将自己训练所需要的数据集上传至服务端指定位置。
  >
  > 退出但不关闭容器：Ctrl+P+Q（如若不行，请参考后面退出-重启容器的方法）。
  > 无法正常使用上述命令，则键入：exit，退出容器，后在命令行中重启容器。
  > 
  > docker attach {server container name}

- 一键运行

  > 在选手替换完自己的代码以及上传数据集后，为了简化编译运行过程，我们提供了一件运行脚本，选手可以前往github下载[一键运行脚本](https://github.com/TOPbuaa/AitransSolution/tree/master).
  >
  > python3 main.py --ip {server ip} --server_name {server container name} --client_name {client container name} --network {network trace path} --block {block trace path}

# Docker 常用命令总结

- 推荐[菜鸟教程](https://www.runoob.com/docker/docker-tutorial.html)

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
