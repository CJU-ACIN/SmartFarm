from yolo.Preprocess_yolo import Preprocess
from cnn.CheckDisease_cnn import CheckDisease
import os
import torch


# Getting Image(matrix)
class Classification:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.yolo_model_dir = '/home/smartfarm/바탕화면/smart_farm_gogo/main/yolo/best2_yolo.pt'
        self.cnn_model_dir = '/home/smartfarm/바탕화면/smart_farm_gogo/main/cnn/resnet50_model_best_cnn.pth'
    
    def predict(self):
        image_pre = Preprocess(self.image_dir, self.yolo_model_dir).cropImage()
        
        name = self.image_dir.split('/')[-1].split('.')[0]
        ext = self.image_dir.split('/')[-1].split('.')[-1]
        print(name)

        boolean_result = []

        for i, img in enumerate(image_pre):
            
            output = CheckDisease(img, self.cnn_model_dir).prediction
            result = '질병' if output else '정상'
            
            print(f'pre_{name}_{i}.{ext} 는 {result} 입니다.')
            # cv2.imwrite(f'results2/pre_{name}_{i}.{ext}', img)
            boolean_result.append(result)

        result = '질병' if '질병' in boolean_result else '정상' 
        
        return result