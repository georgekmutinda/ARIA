from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

def get_train_loader(batch_size : int = 64) -> DataLoader:
    #returns the MNIST  train loader
    
    train_dataset = datasets.FashionMNIST(
        root = "data", 
        train = True, 
        download=True,
        transform = ToTensor()
    )
    
    train_loader = DataLoader(
        dataset = train_dataset,
        batch_size = batch_size,
        shuffle = True,
        num_workers = 2
        
    )
    
    return train_loader

def get_test_loader(batch_size : int =64 ) -> DataLoader:
    test_dataset = datasets.FashionMNIST(
        root="data",
        train = False,
        download = True,
        transform = ToTensor()
        
        
    )
    
    test_loader = DataLoader(
        dataset = test_dataset,
        batch_size = batch_size,
        shuffle = False,
        num_workers= 2
    )
    
    return test_loader
    
