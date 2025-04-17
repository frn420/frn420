import torch
from torchvision import models, transforms
from PIL import Image
import os

# Load class labels
with open("food-101/meta/classes.txt", "r") as f:
    food_classes = [line.strip() for line in f]

# Load pretrained model (ImageNet weights)
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.fc = torch.nn.Linear(model.fc.in_features, 101)  # 101 classes in Food-101
model.eval()

# Use a relative path to the model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.pth")

# Load the model
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))

# Define some sample nutrient data (you can expand this)
sample_nutrients = {
    "pizza": {"Calories": "266 kcal", "Protein": "11 g", "Carbs": "33 g", "Fats": "10 g"},
    "samosa": {"Calories": "262 kcal", "Protein": "6 g", "Carbs": "30 g", "Fats": "15 g"},
    "ice_cream": {"Calories": "207 kcal", "Protein": "3.5 g", "Carbs": "24 g", "Fats": "11 g"},
    "butter_chicken": {"Calories": "438 kcal", "Protein": "30 g", "Carbs": "15 g", "Fats": "30 g"},
}

default_nutrients = {"Calories": "300 kcal", "Protein": "10 g", "Carbs": "40 g", "Fats": "12 g"}

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def predict_nutrients(image_path):
    # Load and preprocess the image
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # Add batch dimension

    # Perform inference
    with torch.no_grad():
        outputs = model(image)
        _, predicted_idx = outputs.max(1)
        food_name = food_classes[predicted_idx.item()]

    # Get nutrient data
    nutrients = sample_nutrients.get(food_name, default_nutrients)
    return food_name, nutrients
