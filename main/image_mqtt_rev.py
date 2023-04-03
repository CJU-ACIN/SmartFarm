import os
import datetime
import threading

import paho.mqtt.client as mqtt
from pymongo import MongoClient

from AI_model import Classification
import Log

logger = Log.create_logger('image')

class Image(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        logger.info(f"sub thread start {threading.currentThread().getName()}")

        path = os.getcwd() + "/static/picture/"
        logger.info(path)

        global count
        count = 0 

        # connect_to = MongoClient("mongodb://203.252.230.243:27017/")
        connect_to = MongoClient("mongodb://localhost:27017/")
        mdb = connect_to.test_db
        collection = mdb.test_data_images
        collection2 = mdb.test_data_images_date # 이미지 날짜  

        now_date = None # 날짜

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("이미지 리시버가 클라이언트와 연결 되었습니다.")
            else:
                logger.info(f"Bad connection Returned code={rc}")


        def on_disconnect(client, userdata, flags, rc=0):
            logger.info("이미지 리시버가 클라이언트와 해제 되었습니다.")


        def on_subscribe(client, userdata, mid, granted_qos):
            logger.info(f"연결 상태 : {str(mid)} {str(granted_qos)}")


        def on_message(client, userdata, msg):
            global count, now_date, now_db_date
            if str(msg.payload) == "b'directory_creat'":
                now = datetime.datetime.now()
                now_date = now.strftime('%Y-%m-%d_%H_%M')
                now_db_date = now.strptime(now_date,'%Y-%m-%d_%H_%M')
                os.mkdir(f"{path}{now_date}")
                logger.info("이미지 폴더 생성")
            elif str(msg.payload) == "b'last_img'": 
                count = 0
                logger.info("마지막 이미지 생성")
            else:
                # 클라이언트에서 받아온 값을 디코딩 
                # cv2.imwrite("./out.jpg", msg)
                logger.info("이미지 생성")
                with open(f'{path}{now_date}/output_{count}.jpg', "wb") as f:
                    f.write(msg.payload)
                logger.info(f"Image Received {count}")

                image_path = f'{path}{now_date}/output_{count}.jpg'

                # 받아온 사진 병충해 여부 판단 
                result = Classification(image_path).predict()

                send_data = image_path.split("/")[3:]
                data = {"image_path":image_path, "image_date": now_db_date, "result": result}
                logger.info(image_path)
                count += 1
                    
                # DB에 저장
                if count == 1 :
                    date_data = {
                        "image_date": now_db_date,
                    }
                    collection2.insert_one(date_data) # 이미지 날짜
                collection.insert_one(data)

        # 새로운 클라이언트 생성
        client = mqtt.Client(client_id = "pc_receive", clean_session= True)

        # 콜백 함수
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.connect('broker.hivemq.com', 1883)

        client.subscribe('/test102234', 1)

        client.loop_forever()

        logger.info(f"sub thread end {threading.currentThread().getName()}")