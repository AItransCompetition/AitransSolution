使用前建议先熟悉[系统与python交互](https://github.com/AItransCompetition/AitransSolution/tree/master/solution_demo/call_python)和[系统使用libtorch](https://github.com/AItransCompetition/AitransSolution/tree/master/solution_demo/call_torch_model)这两个教程，并本地上传好下载的libtorch库和通过如下命令在服务端容器安装好pytorch。

> pip3 install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

本demo是尝试对初赛提供的[强化学习demo](https://github.com/AItransCompetition/DTP_Demo/blob/master/demo_rl_torch.py)进行简化移植的案例，便于选手理解使用，减少了DQN网络的规模。

## demo_rl_torch.py

该文件是对初赛强化学习demo的改写，包括一个简单的Net类（用于训练保存并直接在C++中进行调用的eval_net网络）、DQN类（包含强化学习中所需要的一些变亮和操作），以及一些c++与python交互的函数。

### Net类

同初赛定义，但增加了save函数，主要用于导出c++可直接调用的网络模型，选手可以更改所导出的模型名。

### DQN类

同初赛定义，但把初赛demo中的一些全局变量也放到这个类中，主要为了方便使用pickle序列化以及反序列化，对应save函数和load函数，通过这2两个操作，可以使选手每次与python交互后，把当前的训练参数保存起来，并在下一次调用时继续使用。

### c++与py交互函数

- init_model

初始化DQN模型，并本地保存。

- handle_ip2array

处理由c++传递过来的参数，转换成网络需要的格式和形状。

- model_learn

载入dqn模型，并根据输入的数据进行学习，并将学习结果覆盖保存。选手实际使用时，应注意训练次数与时机，这里为了简单起见，是每次调度cc时都会训练。

- model_decision

载入dqn模型，并根据输入的数据进行决策，类似于后面在c++中直接调用模型，但是该步骤是通过与python交互实现，效率可能没有后者高，仅给选手一个方法，需酌情使用。

## solution.cxx

### 初始化模型

```cpp
system("python3 ./demo/demo_rl_torch.py 1 ./demo/dqn.pkl");
```

### 训练部分

这部分通过命令行传参的方式，将c++这边得到的训练所需要的数据传递给py文件。

```cpp
// construct input
string ip_1, ip_2;
for (int i=0;i < cc_num; i++) {
  ip_1.push_back((char) ('0' + cc_types[i]));

  ip_2 = ip_2 + to_string(rtt_sample[i]);
  if (i+1 < cc_num) {
    ip_1.push_back(',');
    ip_2.push_back(',');
  }

}
// learn and save
string order = "python3 ./demo/demo_rl_torch.py 2 ./demo/dqn.pkl ";
order.append(ip_1);
order.append(" ");
order.append(ip_2);
order.append(" ");
order.append(to_string(*pacing_rate));
cout << order << endl;
// make decision
*pacing_rate = get_number_res_from_order((char *)order.data());
```

### 模型调用部分

为了使算法在模型中更高效的调用，选手所提交的算法不应该再继续训练，而是直接在C++中调用训练完成的模型，因此需要使用libtorch库，以下代码展示了C++中如何调用eval_net的输出模型的过程。

该部分代码在cxx文件中是注释了的，选手需要注意处理。

```cpp
torch::jit::script::Module module;
try
{
  // Deserialize the ScriptModule from a file using torch::jit::load().
  module = torch::jit::load("./demo/eval_net.pt");
  // Create a vector of inputs.
  std::vector<torch::jit::IValue> inputs;
  vector<double> net_input;
  net_input.push_back(*pacing_rate);
  net_input.push_back(loss_nums / cc_num);
  net_input.push_back(rtt_sum / cc_num);
  net_input.push_back(rtt_sample[(int) (cc_num/2)]);
  net_input.push_back(rtt_sample[cc_num-1]);

  torch::Tensor scales_ = torch::tensor(net_input);
  inputs.push_back(scales_);

  // Execute the model and turn its output into a tensor.
  at::Tensor output = module.forward(inputs).toTensor();
  std::cout << output << '\n';
  std::cout << output.argmax() << '\n';

  // judge rate according to net output
  int action = output.argmax().item().toInt();

  std::cout << action << '\n';
  if (action == 0) {
    *pacing_rate = (*pacing_rate) * 1.4;
  }
  else if (action == 1) {
    *pacing_rate = (*pacing_rate) * 1;
  }
  else if (action == 2) {
    *pacing_rate = (*pacing_rate) * 0.4;
  }
  if (*pacing_rate >= your_parameter["MAX_BANDWITH"] || *pacing_rate <= 10*1350*8) {
    *pacing_rate = your_parameter["MAX_BANDWITH"] / 2;
  }
}
catch (const c10::Error &e)
{
  std::cout << e.msg() <<  endl;
  std::cerr << "error loading the model\n";
}
```

