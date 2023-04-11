########################################################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
######################## 작성중 #########################
########################################################
from time import sleep
import json

from flask import Flask, Response
from flask_restx import Api, Resource
from pymongo import MongoClient

from controller import mqtt_controller
import Log

logger = Log.create_logger('test')

my_client = MongoClient()
db = my_client['test_db']

db_col = db.test_data
db_col_actuator = db.test_data_actuator
db_col_images = db.test_data_images
db_col_images_date = db.test_data_images_date
db_col_standlight = db.test_data_standlight

app = Flask(__name__)
api = Api(app)

# 실시간 그래프를 위한 json생성기
@api.route('/graph')
class chartData(Resource):
    # 물 부족 확인 리스트
    global water_list

    water_list =[]
    def get(self, num) :
            
        # mongo db에서 가장 최근 데이터 하나를 불러옴
        raw_data = db_col.find().sort("_id",-1).limit(1)[0]

        # 빗물 감지 센서 => 비오는 여부 판단
        if int(raw_data['rain']) < 1000 :
            rain = "빗물 감지"
        else :
            rain = "빗물 미 감지"

        # 조도 센서 => 밤낮 여부 확인
        if int(raw_data["light"]) > 550 :
            light = "밝음"
        else : 
            light = "어두움"
        
        # 수위 센서
        water_list.append(int(raw_data['water'])) 

        # 물이 부족함
        if len(water_list)>=3 and 0 in water_list :
            water_list.clear()

            water = "물 부족"

            # 일단 10초 동안 물을 보충함 => 최대로 물을 보충 할 수 있게 계산 필요
            with mqtt_controller(10, 'test/send_data') as m:
                m.main()
                logger.info('물을 자동으로 보충합니다.')
        else :
            water = "물 충분함"

        # json 형식
        json_data = {
            'time':str(raw_data["rev_date"]).split(" ")[1],
            'value1':raw_data["temp"],
            'value2':raw_data["humi"],
            'value3':raw_data["light"],
            'value3_1': light, # 조도 센서 텍스트
            'value4' :raw_data['rain'],
            'value4_1' : rain, # 빗물 감지 센서 텍스트
            'value5' : raw_data['water'],
            'value5_1' : water, # 수위 센서 텍스트
        }

        return json_data

@api.route('/other_api')
class actuator(Resource) :
    def get(self) :
        try:
            raw_data_actuator = db_col_actuator.find().sort("_id",-1).limit(1)[0]['actuator']
        except:
            raw_data_actuator = 1

        try:
            image_path = db_col_images.find().sort("_id",-1).limit(1)[0]['image_path']
        except:
            image_path = 'static/picture/None.jpg'

        try:
            raw_data_standlight = db_col_standlight.find().sort("_id",-1).limit(1)[0]['stand_light']
            if raw_data_standlight == 1 :
                raw_data_standlight = "ON" 
            else : 
                raw_data_standlight = "OFF"
        except:
            raw_data_standlight = "OFF"
        
        json_data = {
            'value1' : raw_data_actuator,
            'image_path' : image_path,
            "standlight" : raw_data_standlight,
        }
        return json_data

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7777)
