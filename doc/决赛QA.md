## 提交问题

- 关于提交内容？使用libtorch库的AI算法如何提交？编译了自定义库的算法如何提交？

    与初赛一致，决赛选手需要提交一个带submit文件夹的zip压缩包，其中submit文件夹下，应至少包含solution.cxx和solution.hxx 2个文件。

    使用libtorch库的选手，需要在本地下载libtorch库并上传至服务端:/home/aitrans-server/demo/libtorch目录（提交系统已经安装），并按照教程——[cpp调用torch模型](https://github.com/AItransCompetition/AitransSolution/tree/master/solution_demo/call_torch_model)在本地生成so文件并调试成功后，放置submit目录下一同打包提交。

    使用了自定义库的选手，应在保证不超过提交大小限制并本地编译调试成功的情况下，与submit目录一同打包提交。

- 提交的代码应该注意些什么？

  首先建议上传调试前，关闭算法中所有的io输出，即注释掉所有printf、cout等等输出函数，因为io频繁可能会影响系统运转性能。

  AI算法建议本地完成训练，并调好模型后，上传的算法直接调用模型进行决策，不要再进行训练，同上原因，如果选手拥塞控制算法过于耗时，会导致积留给下次调度的拥塞控制信息越多。

- 官网提交系统“排队人数”是什么意思？

  为了保证选手算法在一个公平稳定的环境下进行测评，决赛提交系统使用“串行跑分”的方式进行测评，因此在官网——代码提交页面，会显示当前正在排队的总人数。其中还会显示选手算法所在排队位置，值为-1表示当前算法正在测评（取决于选手是否提交算法），为0表示是队列的第一个（还未测评，而是下一个测评的算法），然后依次类推。

  因系统是串行的，所有测评会比较耗时，请选手们耐心等候，可随时咨询管理员运行状态。

## 调度1——SolutionSelectBlock问题

- 调度一，就是select_packet函数是什么时候触发？一定是有block的情况下吗？还是说有可能是当前packet_queue为空的情况下也会被触发？

  一定是有block可发的情况下才会调用选手的调度一算法，即blocks链表长度至少为1，block_num值至少为1.

- 调度1结束后的包是会立即被发送出去吗？ 还是说还是受限于CWND或者pacing_rate有可能会再等待一段时间再发送？

  调度结束后就可以发了呢。

- 看demo是比赛调度1（发那个包）的内容改成了发block吗？

  并没有，调度1还是和初赛一致，调度对象只会有不同block的信息，决策结果虽然是block的id，但系统只会发该block划分出来的一个包，如果该block没有发完，那么下次选手调度仍然可以接触到该block的信息。

## 调度2——SolutionCcTrigger问题

- 关于调度2的cwnd（拥塞窗口）和rate（速率）初始值问题？

    系统进行正式发包前需要先与对端进行建连，因此可以第一次调度SolutionCcTrigger时，传递过来的信息是建连数据包带来的信息，所以关于cwnd和rate的初始值都可以在调一次调用SolutionCcTrigger函数时进行特判并设定。

- 在调度2（发多快）中没有时间输入？

  因为系统是真实环境，所以当前时间只需要读取系统时间即可，我们也提供了读取决赛系统当前时间方法的案例————[决赛系统当前时间](https://github.com/AItransCompetition/AitransSolution/blob/master/solution_demo/get_time/test.cxx#L3).

- cc_infos里是什么信息？

  是在当前时刻已经收到，但还未传递给选手处理的拥塞控制信息（包括ack和lost信息）组成的链表。该链表的长度与选手算法复杂度具有一定关系，系统在等待选手算法返回时，会默认使用上一次调度的结果进行运转，而在选手算法决策期间所产生新的拥塞控制信息，会在下一次调度时传递给选手算法。
  而cc_num表示cc_infos链表的长度，可以作为选手遍历链表的上限，避免指针越界。

## 输入输出问题

- 部分变量单位问题

  这个地方选手们需要注意，与初赛统一以包为单位不同，决赛部分输入输出的单位不相同，如rtt、deadline和create time等时间单位是ms单位，变量类型是整数（精度已经足够高）；如输出congestion_window和pacing_rate的单位分别是Bytes和bit/s，初赛代码移植时，前者需要乘上max_packet_size（一个包的粗略大小），后者需要乘上max_packet_size X 8（packet/s -> B/s -> bit/s），同时注意到两个变量都是指针，赋值时需要使用指针运算符“*”（可以参照demo赋值案例）。

  所以选手在进行编写代码时得注意单位转换。s

- 输出的上、下限问题

  选手算法的输出应该考虑上、下限问题，不然可能会导致程序异常运行。

  输出，即congestion_window和pacing_rate，的上限为int类型所能存储的最大值，当某一输出达到这个上限时，其实际效果相当于不再使用输出进行速率限制。

  而下限建议选手使用真实场景中较合理的值，如congestion_window输出不低于"2\*1350"（2个包大小），pacing_rate输出不低于"10\*1350*8"（10包/s）。

- 初赛有些输入在决赛中找不到？

  初赛给予的输入是比较多，但是经过初赛后，我们发现一些输入是不必要的，因此在决赛中，我们对输入进行了简化，但能保证选手算法能够正常移植，如有发现必须要的参数可以联系管理员。

## 本地调试问题

- 如何跑多组数据？AI算法如何设置训练模板？

    AitransSolution仓库中的一键运行脚本每次只提供单组数据（一对block和netwrok）跑多次的功能（指定--run_times参数），所以对于想一次性跑所有数据的选手，需要做一些类似于初赛的操作，如假设所有网络trace都存放在network目录，那么使用reno算法在所有block和network的组合场景中，可以通过如下代码进行全部测试。

    ```python
    # 3 days' blocks
    for block_id in range(3):
      # get all network traces
      for network in os.listdir("./network")
    		# run in dockers that named dtp_server and dtp_client
    		ret = os.popen("python3 main.py --server_name dtp_server --client_name dtp_client --block day%d_train_block.txt --network ./network/%s --run_times 3 --solution_files ../solution_demo/reno/." % (i, network))
        # get qoe_sample from the last line of output
    		qoe_sample = eval(ret.readlines()[-1].split(':')[-1])
    ```

- 使用trace跑出来的分数不一致？

    现在系统对TC的支持有点问题，选手可以现使用ip、server_name和client_name 3个必要参数完成算法的移植，其他参数不声明时默认使用docker镜像中的数据，不声明--network表示不限速。

- client.log是什么内容？bct是什么含义？为什么bct会有负数？

    clinet.log是客户端产生的log信息，其主要信息包括BlockID、bct、BlockSize、Priority和Deadline 5列。
    这里着重强调下bct的含义——block的完成时间，因为客户端和服务端使用的时间会有差异，所以DTP做了时间同步，但可能存在误差，选手可以认为负数近似为0，即block满足deadline。

- client.log中block id不是连续的，有缺失。

    决赛系统的block id使用规则是：从5开始，每次加4。