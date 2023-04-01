import torch
import cv2
class Preprocess:
    def __init__(self, src_dir, model_dir):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_dir)
        
        self.src_image = cv2.imread(src_dir)
        self.xyxy = self.detect()
        
    
    # Detects Lettuce
    def detect(self) -> list:
        # param: model, src_image
        results = self.model(self.src_image)
        
        raw_df = results.pandas().xyxy[0]
        df_lettuce = raw_df[raw_df['name'] == 'lettuce'] # class == lettuce
        df_xyxy = df_lettuce[['xmin', 'ymin', 'xmax', 'ymax']] #xyxy 추출
        
        value = []
        for i in range(len(df_xyxy)):
            data = tuple(map(int, df_xyxy.iloc[i].to_list()))
            value.append(data)
        
        return value # return list of xyxy
    
    
    def cropImage(self):
        # param: xyxy
        images = []
        
        for pos in self.xyxy:
            x1, y1, x2, y2 = pos
            images.append(self.src_image[y1:y2, x1:x2])
        
        return images
    
    
    