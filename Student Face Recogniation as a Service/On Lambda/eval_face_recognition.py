import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from models.inception_resnet_v1 import InceptionResnetV1
from urllib.request import urlopen
from PIL import Image
import json
import numpy as np
import argparse
import build_custom_model
import os
import requests
import pickle
import boto3
from io import BytesIO
import cv2

def handler(event, context):
     dynamodb = boto3.client('dynamodb',region_name='us-east-1')
     s3 = boto3.client('s3',region_name='us-east-1')
     responseSQS = boto3.client("sqs", region_name="us-east-1")
     name_image=event['Records'][0]['s3']['object']['key']
     bucket="cse546group27inputvideobucket"

     labels_dir = "./checkpoint/labels.json"
     model_path = "./checkpoint/model_vggface2_best.pth"
     
     with open(labels_dir) as f:
          labels = json.load(f)
     print(labels)

     device = torch.device('cpu')
     model_file = open('model', 'rb')
     model = pickle.load(model_file)
     
     s3.download_file(bucket, name_image, "/tmp/"+name_image)
     cam = cv2.VideoCapture("/tmp/"+name_image)
     ret, frame = cam.read()
     
     if ret:
          path="/tmp/"+name_image.split(".")[0] + ".png"
          cv2.imwrite(path, frame)
          img=Image.open(path)
     
     img_tensor = transforms.ToTensor()(img).unsqueeze_(0).to(device)
     outputs = model(img_tensor)
     _, predicted = torch.max(outputs.data, 1)
     result = labels[np.array(predicted.cpu())[0]]
     print(result)
     data = dynamodb.get_item(TableName='Info',Key={"Name": {"S": result},"Education":{"S":"Graduate"}})
     print(data)
     
     answer={name_image:[data['Item']['Name']['S'],data['Item']['Education']['S'],data['Item']['Department']['S']]}
     print("Answer",answer)
     
     response = responseSQS.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/472509191780/response-queue",
        MessageBody=json.dumps(answer))
     
     return answer

if __name__ == "__main__":
     parser = argparse.ArgumentParser(description='Evaluate your customized face recognition model')
     parser.add_argument('--img_path', type=str, default="./CSE546_2022Spring_Project2/data/test_me/val/Darshan/image_1.png", help='the path of the dataset')
     args = parser.parse_args()
     img_path = args.img_path
     print(os.getcwd())
     labels_dir = "./checkpoint/labels.json"
     model_path = "./checkpoint/model_vggface2_best.pth"


     # read labels
     with open(labels_dir) as f:
          labels = json.load(f)
     print(f"labels: {labels}")


     device = torch.device('cpu')
     model = build_custom_model.build_model(len(labels)).to(device)
     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'))['model'])
     model.eval()
     print(f"Best accuracy of the loaded model: {torch.load(model_path, map_location=torch.device('cpu'))['best_acc']}")


     img = Image.open(img_path)
     img_tensor = transforms.ToTensor()(img).unsqueeze_(0).to(device)
     outputs = model(img_tensor)
     _, predicted = torch.max(outputs.data, 1)
     result = labels[np.array(predicted.cpu())[0]]
     # print(predicted.data, result)


     img_name = img_path.split("/")[-1]
     img_and_result = f"({img_name}, {result})"
     
     print(f"Image and its recognition result is: {img_and_result}")