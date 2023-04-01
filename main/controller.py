from pickle import TRUE
import paho.mqtt.client as mqtt

class mqtt_controller:
    def __init__(self, val, topic):
        self.val = val
        self.topic = topic

    def __enter__(self):
        print("start.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("end.")

    def main(self):


        def on_connect(client, userdata, flags, rc):
            # 연결이 성공적으로 된다면 완료 메세지 출력
            if rc == 0:
                print("서버와 연결 되었습니다.")
            else:
                print("Bad connection Returned code=", rc)

        # 연결이 끊기면 출력
        def on_disconnect(client, userdata, flags, rc=0):
            print("연결이 종료 되었습니다.")

        def on_publish(client, userdata, mid):
            #print("In on_pub callback mid= ", mid)
            print(f'[{mid}] {userdata}')

        def on_subscribe(client, userdata, mid, granted_qos):
            print("연결 상태 : " + str(mid) + " " + str(granted_qos))

        # 새로운 클라이언트 생성
        client = mqtt.Client()
        # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_publish = on_publish
        # client.on_message = on_message

        # 로컬 아닌, 원격 mqtt broker에 연결
        # address : broker.hivemq.com
        # port: 1883 에 연결
        client.connect('broker.hivemq.com', 1883)
        client.loop_start()
        client.publish(self.topic, str(self.val), 1)
        client.loop_stop()

        # 연결 종료
        client.disconnect()
        # client.loop_forever()

    if __name__ == '__main__':
        main()