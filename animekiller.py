# Deep learning model that detects whether a given image is anime or not
# Classification model
# Trained via a large dataset of anime images 
# Convolutional neural network, archiecture trained off fine-tuned ResNet18
# Freshly trained model had lower accuracy (around 75% compared to 90% of resnet)

# BytesIO for holding the downloaded image bytes
from io import BytesIO

# Requests for reading image from URL
import requests

# Pytorch for the model
import torch

# PIL for image processing
from PIL import Image

# Torchvision for the preprocessing transforms
from torchvision import transforms

from paths import MODEL


# Create a class for the model
class AnimeKiller:

    def __init__(self, path = MODEL, log = True):
        """
        Init takes the model path and sets some variables
        """

        self.log = log
        self.input_size = 224

        self._load_model(path)

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self.input_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def _load_model(self, path):
        self.model = torch.load(path, weights_only = False)
        self.model.eval()
        if self.log:
            print(f"Loaded model at path: {path}")

    def predict(self, image_path):
        """
        Given an image path (URL)
        Returns whether the image is anime or not based on the deep learning model
        """
        # read URL of image
        response = requests.get(image_path)
        response.raise_for_status()
        im = Image.open(BytesIO(response.content))

        # If the image is a GIF, take an average of max 64 frames
        if getattr(im, "is_animated", False):
            num_key_frames = min(im.n_frames, 64)
            X = torch.empty((num_key_frames, 3, self.input_size, self.input_size))
            for i in range(num_key_frames):
                im.seek(im.n_frames * i // num_key_frames)
                X[i, :, :, :] = self.transform(im.convert("RGB"))

            with torch.no_grad():
                outputs = self.model(X)

            _, pred = torch.max(outputs, 1)
            if self.log:
                print("\nGif frame predictions:")
                print(pred)

            return pred.float().mean().item()

        # If it is a regular image, a normal forward pass of the model
        else:
            im = im.convert("RGB")
            X = self.transform(im)

            with torch.no_grad():
                outputs = self.model(X[None, :, :, :])

            probs = torch.sigmoid(outputs).flatten()

            if self.log:
                print(f"probs: {probs}")

            return probs[1].item()
