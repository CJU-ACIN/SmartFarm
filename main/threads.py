from sensor_rev import Sensor
from image_mqtt_rev import Image
import Log

logger = Log.create_logger('threads')
def main():
    t1 = Sensor("Sensor Thread")
    t2 = Image("Image Thread")

    t1.start()
    try:
        t2.start()
    except Exception as e:
        logger.info(e)
        t2.join()
        t1.join()
        return

    t1.join()
    t2.join()

if __name__ == '__main__' :
    while True:
        main()