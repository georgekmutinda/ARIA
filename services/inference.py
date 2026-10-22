from pathlib import Path
import torch
from PIL import Image
from torchvision.transforms import Compose, Grayscale, Resize, ToTensor
from models.cnn_classifier import CNNClassifier

class InferenceService:
    CLASS_NAMES=[
        "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
        "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"   
    ]
    
    def __init__(self, checkpoint_path: str | Path) -> None:
        self.device =torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CNNClassifier().to(self.device)
        checkpoint = torch.load(checkpoint_path, map_location = self.device, weights_only=True)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        self.transform= Compose([
            Grayscale(num_output_channels=1),
            Resize((28,28)),
            ToTensor()
        ])
        
    def predict(self, image:Image.Image)-> tuple[str, float]:
        tensor = self.transform(image)
        tensor =tensor.unsqueeze(0).to(self.device)
        
        with torch.inference_mode():
            logits=self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
            predicted_index = probabilities.argmax(dim=1).item()
            confidence = probabilities[0, predicted_index].item()
            class_name = self.CLASS_NAMES[predicted_index]
            
            return class_name, confidence
            