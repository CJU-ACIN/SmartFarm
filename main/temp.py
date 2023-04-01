import torch

def check_device():
    # cpu or gpu
    if torch.cuda.is_available():
        print('cuda')
    else:
        print('cpu')

check_device()