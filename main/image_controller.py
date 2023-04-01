from pickle import TRUE
import paho.mqtt.client as mqtt

class mqtt_image_start:
    
    def __enter__(self):
        print("start.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("end.")

    def main(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("라즈베리에 이미지 전송 명령을 내렸습니다.")
            else:
                print("연결에 오류가 발생했습니다.", rc)
                
        client = mqtt.Client()      # MQTT Client 오브젝트 생성
        client.on_connect = on_connect
        client.connect(host = 'broker.hivemq.com', port = 1883)    # MQTT 서버에 연결
        client.loop_start()
        client.publish(topic="/test102233",payload= "camera_start", qos= 2)  # 카메라 시작을 알려주는 데이터 전송 
        client.publish(topic="/test102233",payload= "close", qos= 2)  # 카메라 작동 완료
        client.loop_stop()
        client.disconnect()

    if __name__ == '__main__':
        main()
#client.loop(2)        # timeout = 2초