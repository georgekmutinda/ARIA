#The evaluator doesnt know which model it is evaluating. Its purpose is to measure perform



import torch
from data.dataset import get_test_loader
from sklearn.metrics import (confusion_matrix, classification_report)
class Evaluator:
    def __init__(self, model, test_loader, device, class_names):
        self.model = model
        self.test_loader = test_loader
        self.device = device
        self.class_names = class_names

    def evaluate(self):
        self.model.eval()
        correct=0
        total = 0
        all_predictions=[]
        all_labels=[]
        
        with torch.no_grad():
            for images, labels in self.test_loader:
                images=images.to(self.device)
                labels=labels.to(self.device)
                outputs=self.model(images)
                predictions=torch.argmax(outputs, dim=1)
                correct +=(predictions==labels).sum().item()
                total+=labels.size(0)
                all_predictions.append(predictions.cpu())
                all_labels.append(labels.cpu())
                
        all_predictions=torch.cat(all_predictions).numpy()
        all_labels=torch.cat(all_labels).numpy()
                
        cm=confusion_matrix(all_labels, all_predictions)
        report=classification_report(all_labels, all_predictions, target_names=self.class_names)
        accuracy =100 * correct/total
        return {
            "accuracy": accuracy,
            "confusion_matrix": cm,
            "classification_report": report
        }
                