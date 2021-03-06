import torch
from torch import nn
from main import*
import torch.utils.data as Data


device = 'cpu'
#device = 'cuda'

N = 48

def getTrainData():
    train_X, train_Y = read_TrainData('train.csv', N=1)
    torch_dataset = Data.TensorDataset(torch.FloatTensor(train_X),torch.FloatTensor(train_Y))
    loader = Data.DataLoader(
    dataset=torch_dataset,      
    batch_size= N,      
    shuffle=False,               
    num_workers=8,)
    return loader


def getTestData():
    test_X, test_Y = read_TestData('test.csv', N=1)
    return torch.FloatTensor(test_X),torch.FloatTensor(test_Y)

class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        self.rnn = nn.GRU(         
            input_size=19,
            hidden_size=19,         
            num_layers=1,
        )
        self.out = nn.Linear(19, 1)

    def forward(self, x):
        r_out, h_n = self.rnn(x, None)
        out = self.out(r_out)
        return out


try:
    model = torch.load('net.pkl')
except:
    model = RNN()
model.to(device)


loss_func = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(),lr = 1e-5)
epoch = 100
loader = getTrainData()
test_X, test_Y = getTestData()
trainloss = []
testloss = []
for epoch_ in range(epoch):
    for step, (b_x, b_y) in enumerate(loader):       
        b_x = torch.unsqueeze(b_x,dim = 1).to(device)
        output = model(b_x)
        output = torch.squeeze(output,dim=1)
        b_y = b_y.to(device)
        loss = loss_func(output, b_y)
        optimizer.zero_grad()                           
        loss.backward()                                 
        optimizer.step()


        if step % 10000 == 0:
            test_output = model(torch.unsqueeze(test_X,dim=1).to(device))   
            test_output = torch.squeeze(test_output,dim=1) 
                 # (time_step(N), 1 , input_size)
            test_loss = np.mean(((test_output.cpu().detach().numpy()-test_Y.detach().numpy())**2))
            trainloss.append(loss.data.numpy())
            testloss.append(test_loss)
            print('Epoch: ', epoch_, '| train loss: %.4f' % loss.data.cpu().numpy(), '| test loss: %.4f' % test_loss)
            torch.save(model, 'net.pkl')
plotting(trainloss,testloss,'./rnn.png')

    
    
    