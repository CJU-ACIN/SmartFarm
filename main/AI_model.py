from yolo.Preprocess_yolo import Preprocess
from cnn.CheckDisease_cnn import CheckDisease
import Log

logger = Log.create_logger('AI')
# Getting Image(matrix)
class Classification:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.yolo_model_dir = '/home/smartfarm/바탕화면/smart_farm_gogo/main/yolo/best2_yolo.pt'
        self.cnn_model_dir = '/home/smartfarm/바탕화면/smart_farm_gogo/main/cnn/lettuce_resnet50_best.pth'
    
    def predict(self):
        image_pre = Preprocess(self.image_dir, self.yolo_model_dir).cropImage()
        
        name = self.image_dir.split('/')[-1].split('.')[0]
        ext = self.image_dir.split('/')[-1].split('.')[-1]

        boolean_result = set()
        lettuce_status = {
            0: "정상",
            1: "상추균핵병",
            2: "상추노균병"
        }

        for i, img in enumerate(image_pre):
            
            output = CheckDisease(img, self.cnn_model_dir).prediction

            logger.info(f'pre_{name}_{i}.{ext} 는 {lettuce_status[output]} 입니다.')
            # cv2.imwrite(f'results2/pre_{name}_{i}.{ext}', img)
            boolean_result.add(output)

        # 0: 정상, 1: 상추균핵병, 2: 상추노균병


        result = ""
        for i in boolean_result:
            if i == 0:
                result += f"{lettuce_status[i]} "
            elif i == 1:
                result += f"{lettuce_status[i]} "
            elif i == 2:
                result += f"{lettuce_status[i]} "
        # result 결과값
        # 정상, 정상 상추노균병 , 상추균핵병 상추노균병 
        
        logger.info(result)
        
        return result