from sensor_rev import Sensor
from image_mqtt_rev import Image

if __name__ == '__main__' :

    # 센서 값 받아오는 sensor_rev.py 실행
    t1 = Sensor("Sensor Thread")
    t2 = Image("Image Thread")

    t1.start()
    t2.start()
    
    t1.join()
    t2.join()