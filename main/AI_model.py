from yolo.Preprocess_yolo import Preprocess
from cnn.CheckDisease_cnn import CheckDisease
import Log

logger = Log.create_logger('AI')
# Getting Image(matrix)
class Classification:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.yolo_model_dir = '/home/smartfarm/바탕화면/SmartFarm/main/yolo/best2_yolo.pt'
        #self.yolo_model_dir = '/home/smartfarm/바탕화면/SmartFarm/main/yolo/yolo_tomato_lettuce.pt'
        self.lettuce_cnn_model = '/home/smartfarm/바탕화면/SmartFarm/main/cnn/lettuce_resnet50_best.pth'
        self.tomato_cnn_model = '/home/smartfarm/바탕화면/SmartFarm/main/cnn/tomato_resnet50_best.pth'
    
    def predict(self):
        #
        lettuce_image_pre = Preprocess(self.image_dir, self.yolo_model_dir, 'lettuce').cropImage()
        tomato_image_pre = Preprocess(self.image_dir, self.yolo_model_dir, 'tomato').cropImage()
        


        name = self.image_dir.split('/')[-1].split('.')[0]
        ext = self.image_dir.split('/')[-1].split('.')[-1]
        
        # detectable crop diseases
        lettuce_status = {
            0: "정상-상추",
            1: "상추균핵병",
            2: "상추노균병"
        }
        
        toamato_status = {
            0: "정상-토마토",
            1: "토마토곰팡이병",
            2: "토마토황화잎말이병"
        }

        lettuce_boolean_result = set()
        tomato_boolean_result = set()
        ## 질병 판단은 사진에 해당 작물이 있으면 그냥 판단
        ## 이미지에 토마토와 상추 같이 있으면 결과값: 정상-상추, 정상-토마토 일케나옴
        # 상추 질병 판단
        for i, img in enumerate(lettuce_image_pre):
            
            
            output = CheckDisease(img, self.lettuce_cnn_model).prediction

            logger.info(f'pre_{name}_{i}.{ext} 는 {lettuce_status[output]} 입니다.')
            # cv2.imwrite(f'results2/pre_{name}_{i}.{ext}', img)
            lettuce_boolean_result.add(output) # 0: 정상, 1: 상추균핵병, 2: 상추노균병

        
        # 0: 정상, 1: 토마토곰팡이병, 2: 토마토황화잎말이병
        #print(f'{lettuce_boolean_result}')
        #print(f'{tomato_boolean_result}')
        result = ""
        # 상추
        for i in lettuce_boolean_result:
            if i == 0:
                result += f"{lettuce_status[i]} "
            elif i == 1:
                result += f"{lettuce_status[i]} "
            elif i == 2:
                result += f"{lettuce_status[i]} "
        
        # 토마토
        for i in tomato_boolean_result:
            if i == 0:
                result += f"{tomato_status[i]} "
            elif i == 1:
                result += f"{tomato_status[i]} "
            elif i == 2:
                result += f"{tomato_status[i]} "
                
                
        # result 결과값
        # 정상, 정상 상추노균병 , 상추균핵병 상추노균병 
        # 정상, 정상 토마토곰팡이병, 토마토곰팡이병, 토마토황화잎말이병,
        

        # 정상 테스트
        #result = "상추-정상"
        return result 