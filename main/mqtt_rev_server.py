import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime,date
#import asyncio
from time import sleep


#파이썬에서 mongodb로 연결한다. 27017은 mongodb에서 설정한 포트번호
# connect_to = MongoClient("mongodb://203.252.230.243:27017/")
connect_to = MongoClient("mongodb://localhost:27017/")

# connection에서 test_db라는 카테고리 명을 만들고 
# 그 밑에 collection 명을 test_dat으로 생성
mdb = connect_to.test_db
collection = mdb.test_data

# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독), on_message(발행된 메세지가 들어왔을 때)
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[사용 되는건지 확인 필요] 클라이언트와 연결 되었습니다.")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("연결이 해제 되었습니다.")


def on_subscribe(client, userdata, mid, granted_qos):
    print("연결 상태 : " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    
    # 클라이언트에서 받아온 값을 디코딩
    data_split =str(msg.payload.decode("utf-8")).split(" ")
    
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
    print(f"{data_rev_date} => Data 저장 성공")
    #sleep(60)
    print(str(msg.payload.decode("utf-8")))
    #print(data)

# 새로운 클라이언트 생성
client = mqtt.Client()
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
client.subscribe('test/send_data', 1) 

client.loop_forever()
#sleep(60)



    

