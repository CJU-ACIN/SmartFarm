import torch
import torch.nn as nn
import torchvision.transforms as transforms

import numpy as np

import cv2
import gc

### RESNET START ###
# Block class for ResNet
class block(nn.Module):
    def __init__(self, in_channels, out_channels, identity_downsample=None, stride=1):
        
        super(block, self).__init__()
        
        self.expansion = 4
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.conv3 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, padding=0)
        self.bn3 = nn.BatchNorm2d(out_channels*self.expansion)
        
        self.relu = nn.ReLU()
        
        self. identity_downsample = identity_downsample
        
    
    def forward(self, x):
        identity = x
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        
        x = self.conv3(x)
        x - self.bn3(x)
        
        # need to change to shape if dim not same
        if self.identity_downsample is not None:
            identity = self.identity_downsample(identity)
        
        x += identity
        x = self.relu(x)
        
        return x

# CNN Model
class ResNet(nn.Module):
    def __init__(self, block, layers, image_channels, num_classes):
        super(ResNet, self).__init__()
        
        self.in_channels = 64
        self.conv1 = nn.Conv2d(image_channels, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        # ResNet layers
        self.layer1 = self._make_layer(block, layers[0], out_channels=64, stride=1)
        self.layer2 = self._make_layer(block, layers[1], out_channels=128, stride=2)
        self.layer3 = self._make_layer(block, layers[2], out_channels=256, stride=2)
        self.layer4 = self._make_layer(block, layers[3], out_channels=512, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512*4, num_classes)
        

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc(x)
        
        return x
        
        
    def _make_layer(self, block, num_residual_blocks, out_channels, stride):
        identity_downsample = None
        layers = []
        
        # skip
        if stride != 1 or self.in_channels != out_channels * 4:
            identity_downsample = nn.Sequential(nn.Conv2d(self.in_channels, out_channels*4, kernel_size=1,
                                                         stride=stride),
                                               nn.BatchNorm2d(out_channels*4))
        
        # Layers that changes number of channels
        layers.append(block(self.in_channels, out_channels, identity_downsample, stride))
        self.in_channels = out_channels*4
        
        for i in range(num_residual_blocks - 1):
            # 256 channels -> 64, 64*4(256) again
            layers.append(block(self.in_channels, out_channels))
            
        return nn.Sequential(*layers)


# ResNet50
def ResNet50(img_channels=3, num_classes = 2):
    return ResNet(block, [3, 4, 6, 3], img_channels, num_classes)

### RESNET END ###


# check device
def check_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu') # cpu or gpu


# Main Class
class CheckDisease:
    def __init__(self, src_image, model_dir):
        self.device = check_device() # cpu or gpu
        
        # load image matrix
        self.src_image = src_image
        
        # laod model from model_dir
        self.model = self.loadModel(model_dir)

        # 0: disease, 1: normal
        self.prediction = self.checkDisease()

    
    # Load Model
    def loadModel(self, model_dir):
        loaded_model = ResNet50().to(self.device) # empty model
        loaded_model.load_state_dict(torch.load(model_dir, map_location=self.device))

        return loaded_model


    # Classify Normal/Disease
    def checkDisease(self):
        # load image
        src_image = cv2.cvtColor(cv2.resize(self.src_image, (256, 256)), cv2.COLOR_BGR2RGB)
        image = np.array(src_image, dtype=np.uint8)

        transform_norm = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                (0.5, 0.5, 0.5),
                (0.5, 0.5, 0.5)
            )
        ])
        
        transform_org = transforms.Compose([
            transforms.ToTensor(),
        ])

        # normalize and change to torch
        # img_normalized = transform_norm(image).unsqueeze(0).to(self.device)
        img_normalized = transform_org(image).unsqueeze(0).to(self.device)
        self.model.eval() # evaluate mode
        with torch.no_grad():
            output = self.model(img_normalized)
            output_cp = output.cpu().numpy() # copy to detach from cuda

        # free cuda mememory
        del img_normalized
        del self.model
        
        gc.collect()
        torch.cuda.empty_cache()
        # print(torch.cuda.memory_allocated()) # check cuda status

        return output_cp.argmax() # returns highest prediction

    def __str__(self):
        return str(self.prediction)

