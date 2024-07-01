import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, models, transforms

from PIL import Image, GifImagePlugin

import requests
from io import BytesIO


class animeKiller():
    
    def __init__(self, path = "model", threshold = 0.65):
        
        self._load_model(path)
        self.input_size = 224
        self.transform = transforms.Compose([
                transforms.RandomResizedCrop(self.input_size),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        self.threshold = threshold
        

    def _load_model(self, path):
        self.model = torch.load(path)
        print(f"Loaded model at path: /{path}")

    def predict(self, image_path):
        
        # read URL of image
        response = requests.get(image_path)
        im = Image.open(BytesIO(response.content))
        torch.manual_seed(1)

        # If the image is a GIF, take an average of max 64 frames
        if "is_animated" in dir(im) and im.is_animated:
            num_key_frames = min(im.n_frames, 64)
            X = torch.empty((num_key_frames, 3, 224, 224))
            for i in range(num_key_frames):
                im.seek(im.n_frames // num_key_frames * i)
                X[i, :, :, :] = self.transform(im.convert("RGB"))
            
            outputs = self.model(X)
            print(f"outputs: {(outputs)}")
            _, pred = torch.max(outputs, 1)

            print("\nGif frame predictions:")
            print(pred)

            return (pred.float().mean() >= 0.5).item()

        # If it is a regular image, a normal forward pass of the model
        else:
            im = im.convert("RGB")
            X = self.transform(im)
            outputs = self.model(X[None, :, :, :])
            _, pred = torch.max(outputs, 1)
            probs = torch.sigmoid(outputs).flatten()

            print(f"outputs: {(outputs.flatten())}")
            print(f"probs: {(probs.flatten())}")
            print("\nStrict prediction:")
            print(pred)
            print("\nNon-strict prediction:")
            print((outputs[0][1] > self.threshold).item())

            return (probs[1] > self.threshold).item()
