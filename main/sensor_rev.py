from datetime import datetime,date
from time import sleep
import threading

import paho.mqtt.client as mqtt
from pymongo import MongoClient

import Log

logger = Log.create_logger('sensor')

class Sensor(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        logger.info(f"sub thread start {threading.currentThread().getName()}")

        connect_to = MongoClient("mongodb://smartfarm:acin*0446@203.252.230.243:27017/")

        # connection에서 test_db라는 카테고리 명을 만들고 
        # 그 밑에 collection 명을 test_dat으로 생성
        mdb = connect_to.test_db
        mdb2 = connect_to.test_db
        collection = mdb.test_data
        collection2 = mdb2.test_data_actuator

        #파이썬에서 mongodb로 연결한다. 27017은 mongodb에서 설정한 포트번호

        # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독), on_message(발행된 메세지가 들어왔을 때)
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("센서 리시버 클라이언트와 연결 되었습니다.")
            else:
                logger.info(f"Bad connection Returned code={rc}")


        def on_disconnect(client, userdata, flags, rc=0):
            logger.info("센서 리시버 클라이언트와 해제 되었습니다.")
            client.loop_stop()
            client.loop_start()


        def on_subscribe(client, userdata, mid, granted_qos):
            logger.info(f"연결 상태 : {str(mid)} {str(granted_qos)}")


        def on_message(client, userdata, msg):
            # 클라이언트에서 받아온 값을 디코딩
            data_split =str(msg.payload.decode("utf-8")).split(" ")

            logger.info(f"수신 데이터 확인{data_split}")

            if len(data_split) < 4 :

                if "단계" in data_split[0] :
                    logger.info(f"데이터 저장 =>{data_split[0]}")
                    actuator = data_split[0]
                    data = {
                        "actuator" : actuator
                    }
                    collection2.insert_one(data)
                    
                else :
                    pass
            else :
                # 데이터를 수신 받은 시간
                now = datetime.now()
                time = now.strftime('%Y-%m-%d %H:%M:%S')
                data_rev_date = now.strptime(time,'%Y-%m-%d %H:%M:%S')
                
                # 값 분배
                data = {
                        "rev_date" : data_rev_date,
                        "temp": data_split[0],
                        "humi": data_split[1],
                        "light" : data_split[2],
                        "rain" : data_split[3],
                        "water" : data_split[4],
                    }
                # 조도센서는 불켜졌을때와 안켜졌을때를 값을 확인해서 (0,1)로 보내도록 함

                # DB에 data 저장
                collection.insert_one(data)
                #print(data)
        
        # 새로운 클라이언트 생성
        client = mqtt.Client(clean_session= True)
        # 콜백 함수
        
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.connect('broker.hivemq.com', 1883)
        
        client.subscribe('cju_acin_sensor_data', 1) 

        client.loop_forever()

        logger.info(f"sub thread end {threading.currentThread().getName()}")