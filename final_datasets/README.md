# 数据集说明

决赛docker系统所使用的block和network数据集在内容上与初赛一致，但block数据集在形式上有所调整，故选手网络数据集可直接使用初赛的训练集，blocks目录下3个文件的前缀分别表示对应前3天的初赛blocks训练集。

## blocks

| Time(s)  | Deadline(ms) | Block size(Bytes) | Priority |
| -------- | ------------ | ----------------- | -------- |
| 0.0      | 200          | 8295              | 2        |
| 0.021333 | 200          | 2560              | 1        |
| ……       | ……           | ……                | ……       |

- time : 该block的创建时间与上一个block的创建时间之差；
- Deadline ： 该block的有效时间；
- Block size ： 该block的总大小；
- Priority ： 该block的优先级。

## networks

参照官网发布的[初赛网络训练集](https://www.aitrans.online/static/dataset/%E9%A2%84%E8%B5%9B%E9%98%B6%E6%AE%B5%E8%AE%AD%E7%BB%83%E9%9B%86.zip)