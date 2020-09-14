import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import random
import numpy as np
import pickle, sys


# MB -> Mbit -> Kbit -> bit
MAX_BANDWITH = 50*8*1024*1024


class Net(nn.Module):
    '''
    可指定大小的3层torch NN
    '''
    def __init__(self,
                 N_STATES=10,
                 N_ACTIONS=5,
                 N_HIDDEN=30):

        super(Net, self).__init__()

        self.fc1 = nn.Linear(N_STATES, N_HIDDEN)
        self.fc1.weight.data.normal_(0, 0.1)  # initialization
        self.out = nn.Linear(N_HIDDEN, N_ACTIONS)
        self.out.weight.data.normal_(0, 0.1)  # initialization

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        actions_value = self.out(x)
        return actions_value

    def save(self, output=None):
        if not output:
            output = "my_module_model.pt"
        sm = torch.jit.script(self)
        sm.save(output)

    @classmethod
    def load(cls, file):
        return torch.jit.load(file)


class DQN(object):
    def __init__(self,
                 N_STATES=10,
                 N_ACTIONS=5,
                 LR=0.01,
                 GAMMA=0.9,
                 TARGET_REPLACE_ITER=100,
                 MEMORY_CAPACITY=200,
                 BATCH_SIZE=32
                 ):

        self.N_STATES = N_STATES
        self.N_ACTIONS = N_ACTIONS
        self.LR = LR
        # self.EPSILON = EPSILON
        self.GAMMA = GAMMA
        self.TARGET_REPLACE_ITER = TARGET_REPLACE_ITER
        self.MEMORY_CAPACITY = MEMORY_CAPACITY
        self.BATCH_SIZE = BATCH_SIZE

        # some params in RL class
        self.last_state = [0.]*5
        self.last_action = 1
        self.Lambda = 0.9

        self.eval_net = Net(self.N_STATES, self.N_ACTIONS)
        self.target_net = Net(self.N_STATES, self.N_ACTIONS)

        self.learn_step_counter = 0  # 用于 target 更新计时
        self.memory_counter = 0  # 记忆库记数
        self.memory = np.zeros((self.MEMORY_CAPACITY, self.N_STATES * 2 + 2))  # 初始化记忆库
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)  # torch 的优化器
        self.loss_func = nn.MSELoss()  # 误差公式

    def choose_action(self, x):
        x = Variable(torch.unsqueeze(torch.FloatTensor(x), 0))
        # 这里只输入一个 sample
        actions_value = self.eval_net.forward(x)
        action = torch.max(actions_value, 1)[1].data.numpy()[0]  # return the argmax
        return action


    def store_transition(self, s, a, r, s_):
        transition = np.hstack((s, [a, r], s_))
        # 如果记忆库满了, 就覆盖老数据
        index = self.memory_counter % self.MEMORY_CAPACITY
        self.memory[index, :] = transition
        self.memory_counter += 1


    def learn(self):
        # target net 参数更新
        if self.learn_step_counter % self.TARGET_REPLACE_ITER == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
        self.learn_step_counter += 1

        # 抽取记忆库中的批数据
        sample_index = np.random.choice(self.MEMORY_CAPACITY, self.BATCH_SIZE)
        b_memory = self.memory[sample_index, :]
        b_s = Variable(torch.FloatTensor(b_memory[:, :self.N_STATES]))
        b_a = Variable(torch.LongTensor(b_memory[:, self.N_STATES:self.N_STATES+1].astype(int)))
        b_r = Variable(torch.FloatTensor(b_memory[:, self.N_STATES+1:self.N_STATES+2]))
        b_s_ = Variable(torch.FloatTensor(b_memory[:, -self.N_STATES:]))

        # 针对做过的动作b_a, 来选 q_eval 的值, (q_eval 原本有所有动作的值)
        q_eval = self.eval_net(b_s).gather(1, b_a)  # shape (batch, 1)

        q_next = self.target_net(b_s_).detach()  # q_next 不进行反向传递误差, 所以 detach
        q_target = b_r + self.GAMMA * q_next.max(1)[0].reshape(-1, 1)  # shape (batch, 1)
        loss = self.loss_func(q_eval, q_target)

        # 计算, 更新 eval net
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def save(self, files):
        with open(files, "wb") as f:
            pickle.dump(self, f)
        # save eval_net
        self.eval_net.save("./demo/eval_net.pt")
    
    @classmethod
    def load(cls, files):
        with open(files, "rb") as f:
            return pickle.load(f)


def init_model(file):
    # send rate, lost rate, rtt measure
    N_F = 1 + 2 + 2
    # 1.4,1.1,0.4
    N_A = 3 

    dqn = DQN(N_STATES=N_F,
                        N_ACTIONS=N_A,
                        LR=0.01,
                        GAMMA=0.9,
                        TARGET_REPLACE_ITER=100,
                        MEMORY_CAPACITY=500,
                        BATCH_SIZE=32
                    )

    dqn.save(file)


def handle_ip2array(ip_data):
    cc_types = ip_data["cc_types"]
    rtt_sample = ip_data["rtt_sample"]
    pacing_rate = ip_data["pacing_rate"]

    cc_num = len(cc_types)

    instant_loss_rate = sum(cc_types) / cc_num
    # mean, middle, latest
    rtt_measure = [np.mean(rtt_sample), rtt_sample[len(rtt_sample) // 2], rtt_sample[-1]]

    # current state
    s_ = []
    s_.append(pacing_rate / MAX_BANDWITH)
    s_.append(instant_loss_rate)
    s_.extend(rtt_measure)

    return s_


def model_learn(ip_data, file):
    dqn = DQN.load(file)
    
    pacing_rate = ip_data["pacing_rate"]
    cc_num = len(cc_types)
    # reward
    reward = 0
    for i in range(cc_num):
        if cc_types[i] == 0:
            reward += pacing_rate * (i+1)
        else:
            reward -= pacing_rate * (i+1)

    # current state
    s_ = handle_ip2array(ip_data)
    s_array = np.array(s_)

    # store trasition
    dqn.store_transition(dqn.last_state, dqn.last_action, reward, s_array)

    # choose action
    a = dqn.choose_action(s_array)

    # exploration
    if random.random() < dqn.Lambda:
        a = random.randint(0,2)
    if pacing_rate - 500*1350*8 < 0.00001:
        pacing_rate = MAX_BANDWITH / 2
        a = 0
    elif MAX_BANDWITH - pacing_rate < 1.0000001:
        pacing_rate = MAX_BANDWITH / 2
        a = 2
    elif a == 0:
        pacing_rate *= 1.4
    elif a == 1:
        pacing_rate *= 1.
    else:
        pacing_rate *= 0.4
    dqn.last_action = a
   
    # DQN learn
    dqn.learn()
    dqn.last_state = s_
    dqn.save(file)
    print(pacing_rate)


def model_decision(ip_data, file):
    dqn = DQN.load(file)

    s_array = handle_ip2array(ip_data)
    ret = dqn.choose_action(s_array)
    print(ret)


if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == '0':
        print("Hello python3!")

    elif mode == '1':
        init_model(sys.argv[2])

    elif mode in ['2', '3']:
        '''
        input : 2 0,1,0,0 10,20,30,20 5000
        '''
        cc_types = list(map(lambda x: int(x), sys.argv[3].split(',')))
        rtt_sample = list(map(lambda x: int(x), sys.argv[4].split(',')))
        pacing_rate = int(sys.argv[5])
        ip = {
            "cc_types" : cc_types,
            "rtt_sample" : rtt_sample,
            "pacing_rate" : pacing_rate
        }

        if mode == '2':
            model_learn(ip, sys.argv[2])

        if mode == '3':
            print(model_decision(ip, sys.argv[2]))
        