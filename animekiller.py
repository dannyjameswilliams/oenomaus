# Deep learning model that detects whether a given image is anime or not
# Classification model
# Trained via a large dataset of anime images 
# Convolutional neural network, archiecture trained off fine-tuned ResNet18
# Freshly trained model had lower accuracy (around 75% compared to 90% of resnet)

# Pytorch for the model
import torch
from torchvision import transforms

# PIL for image processing
from PIL import Image

# Requests for reading image from URL
import requests
from io import BytesIO

# Create a class for the model
class animeKiller():
    
    def __init__(self, path = "model", threshold = 0.65, log = True):
        """
        Init takes model relative path and sets some variables
        threshold: float, default 0.65 - if probability of being anime is greater than this, it is considered anime. default at 0.65 is to remove more false positives
        """
        
        self.log = log
        self.threshold = threshold
        self.input_size = 224
        
        self._load_model(path)
        
        self.transform = transforms.Compose([
                transforms.RandomResizedCrop(self.input_size),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        
        
        

    def _load_model(self, path):
        self.model = torch.load(path)
        if self.log:
            print(f"Loaded model at path: /{path}")

    def predict(self, image_path):
        """
        Given an image path (URL)
        Returns whether the image is anime or not based on the deep learning model
        """
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
            
            _, pred = torch.max(outputs, 1)
            if self.log:
                print(f"outputs: {(outputs)}")
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

            if self.log:
                print(f"outputs: {(outputs.flatten())}")
                print(f"probs: {(probs.flatten())}")
                print("\nStrict prediction:")
                print(pred)
                print("\nNon-strict prediction:")
                print((outputs[0][1] > self.threshold).item())

            return (probs[1] > self.threshold).item()
