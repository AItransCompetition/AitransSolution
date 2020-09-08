
# 输入

| 变量名                 | 含义                                     | 初赛对应量        |
| ---------------------- | ---------------------------------------- | ----------------- |
| init_congestion_window | 初始拥塞窗口大小                         | init -- cwnd      |
| init_pacing_rate       | 初始发送速率                             | Init -- send_rate |
| blocks                 | 当前可发的block组成的信息                | packet_queue      |
| block_num              | blocks链表长度                           | len(packet_queue) |
| next_packet_id         | 会分配给当前决策结果的包的ID             |                   |
| current_time           | 当前时间（ms）                           | cur_time          |
| cc_infos               | 当前时刻还未处理的拥塞控制相关的一些信息 |                   |
| cc_num                 | cc_infos链表的长度                       |                   |
| pacing_rate            | 发送速率（bit /s）                       | send_rate         |
| congestion_window      | 拥塞窗口大小（Bytes）                    | cwnd              |

## 输入-blocks


| 变量名            | 含义                       | 初赛对应量                |
| ----------------- | -------------------------- | ------------------------- |
| block_id          | 当前block的ID              | block_info -- Block_id    |
| block_deadline    | deadline（ms）             | block_info -- Deadline    |
| block_priority    | 优先级                     | block_info -- Priority    |
| block_create_time | 创建时间（ms）             | block_info -- Create_time |
| block_size        | block总大小（Bytes）       | block_info -- Size        |
| remaining_size    | 该block的剩余大小（Bytes） |                           |

## 输入-cc_infos

| 变量名          | 含义                                      | 初赛对应量                                           |
| --------------- | ----------------------------------------- | ---------------------------------------------------- |
| event_type      | 取值'D'和'F'，分别表示丢包事件和ack包事件 | data -- event_type                                   |
| rtt             | 往返时延（ms）                            | data -- packet_information_dict -- Latency           |
| bytes_in_flight | 发送端已发出但未收到反馈的字节数（Bytes） | data -- packet_information_dict -- Extra -- inflight |
| event_time      | 当前ack或lost事件具体发生的时间           |                                                      |
| packet_id       | 当前ack或lost事件对应的包ID               |                                                      |

------



---
---
# 示例
## 1. 启发式算法

选手只需要将初赛所写的python代码，转写成c++代码即可。

我们已经对初赛所提供的reno demo进行了决赛系统的转写，可以参照[决赛系统-reno demo](https://github.com/TOPbuaa/AitransSolution/tree/tc_tool/src/aitrans/reno)。

## 2. 与python代码的交互

部分选手对python的一些语法特性、库具有依赖（dict、numpy等等）,为此我们提供了关于C++与python交互的一些使用案例，可以参照[决赛算法与python的交互](https://github.com/TOPbuaa/AitransSolution/tree/tc_tool/src/aitrans/call_python)

## 3. AI算法

选手应在本地使用所提供的docker决赛系统和训练集进行训练，并使用深度学习框架所提供的[ONNX](https://zh.wikipedia.org/wiki/ONNX)（Open Neural Network Exchange，开放式网络交换）模型导出API，及时导出ONNX模型，选手所提交的算法应包括原始数据适应网络输入的处理、调用onnx模型进行决策等等，但不应该进行在线训练。

具体模型导出方法以及C++调用方法可以参照[pytorch官方文档](https://pytorch.org/tutorials/advanced/cpp_export.html)