import os
import datetime
import threading

import paho.mqtt.client as mqtt
from pymongo import MongoClient

from AI_model import Classification

class Image(threading.Thread):
    def run(self):
        path = os.getcwd() + "/static/picture/"
        print(path)
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
                print("이미지 클라이언트와 연결 되었습니다.")
            else:
                print("Bad connection Returned code=", rc)


        def on_disconnect(client, userdata, flags, rc=0):
            print("연결이 해제 되었습니다.")


        def on_subscribe(client, userdata, mid, granted_qos):
            print("연결 상태 : " + str(mid) + " " + str(granted_qos))


        def on_message(client, userdata, msg):
            global count, now_date, now_db_date
            if str(msg.payload) == "b'directory_creat'":
                now = datetime.datetime.now()
                now_date = now.strftime('%Y-%m-%d_%H_%M')
                now_db_date = now.strptime(now_date,'%Y-%m-%d_%H_%M')
                os.mkdir(f"{path}{now_date}")
                print("이미지 폴더 생성")
            elif str(msg.payload) == "b'last_img'": 
                count = 0
                print("마지막 이미지 생성")
            else:
                # 클라이언트에서 받아온 값을 디코딩 
                # cv2.imwrite("./out.jpg", msg)
                print("이미지 생성")
                f = open(f'{path}{now_date}/output_{count}.jpg', "wb")
                f.write(msg.payload)
                print(f"Image Received {count}")
                f.close()
                image_path = f'{path}{now_date}/output_{count}.jpg'

                # 받아온 사진 병충해 여부 판단 
                result = Classification(image_path).predict()

                send_data = image_path.split("/")[3:]
                data = {"image_path":image_path, "image_date": now_db_date, "result": result}
                print(image_path)
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
        # 로컬 아닌, 원격 mqtt broker에 연결
        # address : broker.hivemq.com
        # port: 1883 에 연결
        client.connect('broker.hivemq.com', 1883)
        # test/send_data 라는 topic 구독
        client.subscribe('/test102234', 2)
        client.loop_forever()