import torch
import torch.nn as nn
import torch.nn.functional as F

class Tnet(nn.Module):
    def __init__(self, k=3, device="cpu"):
        super().__init__()
        self.k=k
        self.conv1 = nn.Conv1d(k,64,1)
        self.conv2 = nn.Conv1d(64,128,1)
        self.conv3 = nn.Conv1d(128,1024,1)
        self.fc1 = nn.Linear(1024,512)
        self.fc2 = nn.Linear(512,256)
        self.fc3 = nn.Linear(256,k*k)

        self.bn1 = nn.BatchNorm1d(64)
        self.bn2 = nn.BatchNorm1d(128)
        self.bn3 = nn.BatchNorm1d(1024)
        self.bn4 = nn.BatchNorm1d(512)
        self.bn5 = nn.BatchNorm1d(256)

        self.device = device


    def forward(self, input):
        # input.shape == (bs,n,3)
        bs = input.size(0)
        xb = F.relu(self.bn1(self.conv1(input)))
        xb = F.relu(self.bn2(self.conv2(xb)))
        xb = F.relu(self.bn3(self.conv3(xb)))
        pool = nn.MaxPool1d(xb.size(-1))(xb)
        flat = nn.Flatten(1)(pool)
        xb = F.relu(self.bn4(self.fc1(flat)))
        xb = F.relu(self.bn5(self.fc2(xb)))

        #initialize as identity
        init = torch.eye(self.k, requires_grad=True).repeat(bs,1,1)
        init=init.to(self.device)

        matrix = self.fc3(xb).view(-1,self.k,self.k) + init
        return matrix


class Transform(nn.Module):
    def __init__(self, device):
        super().__init__()
        self.input_transform = Tnet(k=3, device=device)
        self.feature_transform = Tnet(k=64, device=device)
        self.conv1 = nn.Conv1d(3,64,1)

        self.conv2 = nn.Conv1d(64,128,1)
        self.conv3 = nn.Conv1d(128,1024,1)

        self.bn1 = nn.BatchNorm1d(64)
        self.bn2 = nn.BatchNorm1d(128)
        self.bn3 = nn.BatchNorm1d(1024)

    def forward(self, input):
        matrix3x3 = self.input_transform(input)
        # batch matrix multiplication
        xb = torch.bmm(torch.transpose(input,1,2), matrix3x3).transpose(1,2)

        xb = F.relu(self.bn1(self.conv1(xb)))

        matrix64x64 = self.feature_transform(xb)
        xb = torch.bmm(torch.transpose(xb,1,2), matrix64x64).transpose(1,2)

        xb = F.relu(self.bn2(self.conv2(xb)))
        xb = self.bn3(self.conv3(xb))
        xb = nn.MaxPool1d(xb.size(-1))(xb)
        output = nn.Flatten(1)(xb)
        return output, matrix3x3, matrix64x64

class PointNet(nn.Module):
    def __init__(self, classes, device):
        super().__init__()
        self.transform = Transform(device)
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, classes)

        self.bn1 = nn.BatchNorm1d(512)
        self.bn2 = nn.BatchNorm1d(256)
        self.dropout = nn.Dropout(p=0.3)
        self.logsoftmax = nn.LogSoftmax(dim=1)

        self.device = device

    def forward(self, input):
        xb, matrix3x3, matrix64x64 = self.transform(input)
        xb = F.relu(self.bn1(self.fc1(xb)))
        xb = F.relu(self.bn2(self.dropout(self.fc2(xb))))
        output = self.fc3(xb)
        return self.logsoftmax(output), matrix3x3, matrix64x64

    def load_from_pth(self, path):
        self.load_state_dict(torch.load(path, map_location=self.device))
        self.to(self.device)

def pointnetloss(outputs, labels, m3x3, m64x64, device, alpha = 0.0001):
    criterion = torch.nn.NLLLoss()
    bs=outputs.size(0)
    id3x3 = torch.eye(3, requires_grad=True).repeat(bs,1,1).to(device)
    id64x64 = torch.eye(64, requires_grad=True).repeat(bs,1,1).to(device)
    diff3x3 = id3x3-torch.bmm(m3x3,m3x3.transpose(1,2))
    diff64x64 = id64x64-torch.bmm(m64x64,m64x64.transpose(1,2))
    return criterion(outputs, labels) + alpha * (torch.norm(diff3x3)+torch.norm(diff64x64)) / float(bs)

def train_model(model, train_loader, valid_loader, save_path, epochs=4, device="mps"):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.00025)

    def train(model, train_loader, val_loader, epochs):
        for epoch in range(epochs): 
            model.train()
            running_loss = 0.0
            print_every_x = 16
            for i, data in enumerate(train_loader, 0):
                inputs = data['data'].to(device)
                labels = data['label'].to(device)
                optimizer.zero_grad()
                outputs, m3x3, m64x64 = model(inputs.transpose(1,2))

                loss = pointnetloss(outputs, labels, m3x3, m64x64, device)
                loss.backward()
                optimizer.step()

                # print statistics
                running_loss += loss.item()
                if i % print_every_x == print_every_x - 1:
                    print('[Epoch: %d, Batch: %4d / %4d], loss: %.3f' %
                        (epoch + 1, i + 1, len(train_loader), running_loss / 10))
                    running_loss = 0.0

            model.eval()
            correct = total = 0

            # validation
            if val_loader:
                with torch.no_grad():
                    for data in val_loader:
                        inputs, labels = data['data'].to(device).float(), data['label'].to(device)
                        outputs, __, __ = model(inputs.transpose(1,2))
                        _, predicted = torch.max(outputs.data, 1)
                        total += labels.size(0)
                        correct += (predicted == labels).sum().item()
                val_acc = 100. * correct / total
                print('Valid accuracy: %d %%' % val_acc)

            # save the model
            torch.save(model.state_dict(), save_path)

    train(model, train_loader, valid_loader, epochs=epochs)

def eval_model(model, input, id2label, device):
    model.eval()
    with torch.no_grad():
        # Convert from 42x3 to 1x42x3
        input = input.unsqueeze(0).to(device)
        outputs, __, __ = model(input.transpose(1,2))

        # Softmax over logits
        probs = torch.exp(outputs)

        # Get the top class of the output
        top_p, top_class = probs.topk(1, dim=1)

        # Get the probability of the top class
        label = id2label[top_class.item()]
        probability = int(top_p.item() * 100)

        return label, probability
        