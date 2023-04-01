from flask import *
from pymongo import MongoClient
from datetime import datetime, timedelta
from time import sleep
from controller import mqtt_controller
from sensor_rev import Sensor
from threading import Thread
import json, math
from image_controller import mqtt_image_start
from image_mqtt_rev import Image
from light_controller import mqtt_standlight

app = Flask(__name__)

# 몽고 DB 연결
# my_client = MongoClient("mongodb://203.252.230.243:27017/")
my_client = MongoClient()
db = my_client['test_db']

db_col = db.test_data
db_col_actuator = db.test_data_actuator
db_col_images = db.test_data_images
db_col_images_date = db.test_data_images_date
db_col_standlight = db.test_data_standlight

# 메인 페이지
@app.route('/',methods=['POST','GET'])
def graph() :

    # 처음 30분 데이터
    first_data_graph = db_col.find().sort("_id",-1).limit(1)[0:30]

    if request.method == 'POST':

        try : # 창문 환기 시스템에 값을 전달 헀을때
            val1 = None
            val2 = str(request.form['length'])

            if request.form['button'] == 'close':
                val1 = 'close'
            elif request.form['button'] == 'open':
                val1 = 'open'

            val = val1 +" "+ val2
            print(val)
            with mqtt_controller(val,'test/actuator') as m:
                m.main()

        except : # 창문 환기 시스템에 값을 전달하지 않았을때
            pass

        try : # 수중 모터(물주기)를 작동시켰을때
            val = int(request.form['water_active'])

            if request.form['button'] == '물 주기':
                with mqtt_controller(val, 'test/send_data') as m:
                    m.main()
                    print("물 주기")

        except : # 수중 모터(물주기)를 작동시키지 않았을때
            pass

        try : 
            if request.form['button'] == '사진':
                with mqtt_image_start() as m:
                    m.main()
                    print("사진 찍기를 시작합니다.")
        except :
            pass

        try : 
            if request.form['button'] == 'ON':
                val = request.form['button']

                with mqtt_standlight(val) as m:
                    m.main()
                    data = {"stand_light" : 1}
                    print("불을 켰습니다")

            elif request.form['button'] == 'OFF':
                val = request.form['button']
                
                with mqtt_standlight(val) as m:
                    m.main()
                    data = {"stand_light" : 0}
                    print("불을 껐습니다")
            
            db_col_standlight.insert_one(data)
            print("[조명] 작업 완료")

        except :
            pass

    return render_template('index.html',first_data_graph = first_data_graph)

@app.route('/sensor_db',methods=['POST','GET'])
def sensor_db() :
    limit = 10 # DB 테이블 몇개 보여줄지
    block_size = 10 # 페이지네이션 블럭 개수
    
    if request.method == 'POST':
        page = request.args.get('page', type=int, default=1)  # 페이지
        
        try : # DB 조회 버튼을 눌렀을때
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            
        except : # DB 조회 버튼을 누르지 않았을때
            today = datetime.today()
            start_date = db_col.find_one()['rev_date']
            start_date = str(start_date).split(" ")[0]
            end_date = (today+timedelta(days=1)).strftime("%Y-%m-%d")

    if request.method == 'GET':
        today = datetime.today()
        start_date = db_col.find_one()['rev_date']
        start_date = str(start_date).split(" ")[0]
        end_date = (today+timedelta(days=1)).strftime("%Y-%m-%d")

        start_date = request.args.get('start_date', type=str, default=start_date)
        end_date = request.args.get('end_date', type=str, default=end_date)
        page = request.args.get('page', type=int, default=1)  # 페이지
    
    # DB 조회를 위한 날짜 처리    
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    send_start_date = str(start_date).split(" ")[0]
    send_end_date = str(end_date).split(" ")[0]

    # 해당 날짜의 데이터를 DB에서 가져오기
    results = db_col.find({"rev_date": {"$gte": start_date, "$lte": end_date}}).sort("_id",-1).skip((page-1)*limit).limit(limit)
    total_data  = db_col.count_documents({"rev_date": {"$gte": start_date, "$lte": end_date}})
    
    # 페이지네이션 처리
    last_page_num = math.ceil(total_data / limit) 
    block_num = int((page - 1) / block_size)
    block_start = (block_size * block_num) + 1
    block_end = block_start + (block_size - 1)

    return render_template('sensor_db.html',data=results,start_date = send_start_date ,end_date = send_end_date,limit=limit,page=page,block_start=block_start,block_end=block_end,last_page_num=last_page_num,total_data=total_data)

@app.route('/image_db',methods=['POST','GET'])
def image_db() :
    limit = 10 # DB 테이블 몇개 보여줄지
    block_size = 10 # 페이지네이션 블럭 개수

    if request.method == 'POST':
        page = request.args.get('page', type=int, default=1)  # 페이지
        
        try : # DB 조회 버튼을 눌렀을때
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            
        except : # DB 조회 버튼을 누르지 않았을때
            today = datetime.today()
            start_date = db_col_images_date.find_one()['image_date']
            start_date = str(start_date).split(" ")[0]
            end_date = (today+timedelta(days=1)).strftime("%Y-%m-%d")
    
    if request.method == 'GET':
        today = datetime.today()
        start_date = db_col_images_date.find_one()['image_date']
        start_date = str(start_date).split(" ")[0]
        end_date = (today+timedelta(days=1)).strftime("%Y-%m-%d")

        start_date = request.args.get('start_date', type=str, default=start_date)
        end_date = request.args.get('end_date', type=str, default=end_date)
        page = request.args.get('page', type=int, default=1)  # 페이지

    #results = db_col_images.find().sort("_id",-1)
    #results2  = db_col_images_date.find().sort("_id",-1)

    # DB 조회를 위한 날짜 처리    
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    print(f'{start_date}, {end_date}')

    send_start_date = str(start_date).split(" ")[0]
    send_end_date = str(end_date).split(" ")[0]

    # 해당 날짜의 데이터를 DB에서 가져오기
    results = db_col_images_date.find({"image_date": {"$gte": start_date, "$lte": end_date}}).sort("_id",-1).skip((page-1)*limit).limit(limit)
    total_data  = db_col_images_date.count_documents({"image_date": {"$gte": start_date, "$lte": end_date}})
    
    # 페이지네이션 처리
    last_page_num = math.ceil(total_data / limit) 
    block_num = int((page - 1) / block_size)
    block_start = (block_size * block_num) + 1
    block_end = block_start + (block_size - 1)
    
    return render_template('image_db.html',date_data=results, start_date=send_start_date, end_date=send_end_date, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num, total_data=total_data)

@app.route('/image_db/<image_date>',methods=['POST','GET'])
def image_detail(image_date) :
    if request.method == 'GET':
        image_date = datetime.strptime(image_date, "%Y-%m-%d %H:%M:00")
        start_image_date = (image_date-timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:00")
        start_image_date = datetime.strptime(start_image_date, "%Y-%m-%d %H:%M:00")

    image_data = db_col_images.find({"image_date": {"$gte": start_image_date, "$lte": image_date}}).sort("_id",-1) # 해당 날짜의 사진들
    #image_result = db_col_images.find({"result": {"$gte": start_image_date, "$lte": image_date}}).sort("_id",-1) # 병충해 여부
    sensor_data = db_col.find({"rev_date": {"$gte": start_image_date, "$lte":image_date}}).sort("_id",-1).limit(1)

    #print(f'{image_data}, {image_result}, {sensor_data}')
    
    return render_template('image_db_detail.html', data=image_data, sensor_data = sensor_data, date = image_date)
   
# 실시간 그래프를 위한 json생성기
@app.route('/graph')
def chart_data() :
    # 물 부족 확인 리스트
    water_list =[]
    def generate_raw_data() :
            
        # mongo db에서 가장 최근 데이터 하나를 불러옴
        raw_data = db_col.find().sort("_id",-1).limit(1)[0]
        #print(raw_data)

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
                print("물을 자동으로 보충합니다.")
        else :
            water = "물 충분함"

        # json 형식
        json_data = json.dumps({'time':str(raw_data["rev_date"]).split(" ")[1],
        'value1':raw_data["temp"],
        'value2':raw_data["humi"],
        'value3':raw_data["light"],
        'value4' :raw_data['rain'],
        'value4_1' : rain, # 빗물 감지 센서 텍스트
        'value3_1': light, # 조도 센서 텍스트
        'value5' : raw_data['water'],
        'value5_1' : water,
        }) # 수위 센서 텍스트
        
        yield f"data: {json_data}\n\n"
        sleep(60)
        # sleep(61)  # 1분 마다 json 값 생성

    return Response(generate_raw_data(), mimetype='text/event-stream')

@app.route('/other_api')
def actuator() :
    def generate_raw_data() :
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
        
        json_data = json.dumps({
            'value1' : raw_data_actuator,
            'image_path' : image_path,
            "standlight" : raw_data_standlight,
        })
        yield f"data: {json_data}\n\n"
        sleep(5)
    return Response(generate_raw_data(), mimetype='text/event-stream')

if __name__ == '__main__' :

    # 센서 값 받아오는 sensor_rev.py 실행
    temp = Sensor()
    temp.daemon = False
    temp.start()

    temp2 = Image()
    temp2.daemon = False
    temp2.start()

    # 플라스크 실행
    kwargs = {'threaded':True, 'debug':True}
    flaskThread = Thread(target=app.run(), daemon=True, kwargs=kwargs).start()
    # app.run(host= "0.0.0.0", debug=True, port=9999, threaded = True)