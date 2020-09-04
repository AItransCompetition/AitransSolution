import torch
import torch.nn.functional as F


# define network
class MyModule(torch.nn.Module):
    def __init__(self, N, M):
        super(MyModule, self).__init__()
        self.fc1 = torch.nn.Linear(N, M)
        self.fc1.weight.data.normal_(0, 0.1)  # initialization

    def forward(self, input):
        output = self.fc1(input)

        return F.relu(output)


# instance
my_module = MyModule(10,20)

# save model
sm = torch.jit.script(my_module)
sm.save("my_module_model.pt")