import torch
import torch.nn as nn
from torchvision import models

class CheXNet(nn.Module):
    def __init__(self):
        super(CheXNet, self).__init__()
        self.densenet = models.densenet121(pretrained=False)
        num_ftrs = self.densenet.classifier.in_features
        self.densenet.classifier = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.densenet(x)

def load_model(path="models/best_chexnet.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = CheXNet().to(device)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model, device