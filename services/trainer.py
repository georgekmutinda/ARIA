#Purpose is to learn

import torch
import torch.nn as nn
import torch.optim as optim
import os

from data.dataset import get_train_loader
from models.cnn_classifier import CNNClassifier

class Trainer:
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CNNClassifier().to(self.device)
        self.train_loader = get_train_loader()
        self.loss_fn  = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr = 0.01
        )
        
        
    def train (self, epochs = 5):
        print(self.model)
        
        self.model.train()
        
        for epoch in range(epochs):
            running_loss = 0
            
            for images, labels in self.train_loader:
                images  = images.to(self.device)
                labels = labels.to(self.device)
                
                self.optimizer.zero_grad()
                predictions = self.model(images)
                loss = self.loss_fn(predictions, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()
            print(
                f"Epoch {epoch+1}/{epochs} |"
                f"Loss: {running_loss/len(self.train_loader): .4f}"
            )
        os.makedirs("checkpoints", exist_ok = True)
        torch.save(self.model.state_dict(), "checkpoints/ simple_classifier.pth")   
        print("Model weights saved successfully to checkpoints/simple_classifier.pth") 
    
            