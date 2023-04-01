/*!
    * Start Bootstrap - SB Admin v7.0.5 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2022 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

//const source = new EventSource("/graph")

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

$(document).ready(function() {
    const config_graph  ={
        type: 'line',
        data: {
            labels : [],
            datasets : [{
                label : "Temperature",
                yAxisID: "A",
                backgroundColor : 'rgb(255,51,51)',
                borderColor: 'rgb(255,51,51)',
                data : [],
                fill : false,
            },{
                label : "humi",
                yAxisID: "B",
                backgroundColor : 'rgb(51,153,255)',
                borderColor: 'rgb(51,153,255)',
                data : [],
                fill : false,
            }]
        },
        options : {
            responsive : true,
            title : {
                display : true,
                text : "실시간 온습도 센서 값"
            },
            scales : {
                xAxes : [{
                    display : true,
                    scaleLabel : {
                        display : true,
                        labelString: '시간'
                    }
                }],
                yAxes : [{
                    id: 'A',
                    display : true,
                    scaleLabel : {
                        display : true,
                        labelString: '온도'
                    }
                },{
                    id: 'B',
                    position: 'right',
                    display : true,
                    scaleLabel : {
                        display : true,
                        labelString: '습도'
                    }
                }
            ]
            },
            tooltips: {
                mode : 'index',
                intersect : false,
            },
            hover : {
                mode: 'nearest',
                intersect: true
            },
        }
    };
    const config_light ={
        type: 'doughnut',
        data : {
            labels: ['조도센서','남은 센서 값'],//['온도센서','습도센서','조도센서', '빗물감지 센서'],
            datasets: [{
                data: [],
                backgroundColor: ['rgb(255, 255, 51)','rgb(255,255,255)'],//,'rgb(255, 255, 51)', 'rgb(204, 229, 255)'],
                borderColor : 'rgb(150,150,150)',
            }],
        },
        options: {
            responsive: false,
            cutoutPercentage : 50,
            rotation: 1 * Math.PI,
            circumference: 1 * Math.PI
        },
    };
    const config_temp ={
        type: 'doughnut',
        data : {
            labels: ['온도센서','남은 센서 값'],//['온도센서','습도센서','조도센서', '빗물감지 센서'],
            datasets: [{
                data: [],
                backgroundColor: ['rgb(255,51,51)','rgb(255,255,255)'],//,'rgb(255, 255, 51)', 'rgb(204, 229, 255)'],
                borderColor : 'rgb(150,150,150)',
            }],
        },
        options: {
            responsive: false,
            cutoutPercentage : 50,
            rotation: 1 * Math.PI,
            circumference: 1 * Math.PI
        },
    };
    const config_humi ={
        type: 'doughnut',
        data : {
            labels: ['습도센서','남은 센서 값'],//['온도센서','습도센서','조도센서', '빗물감지 센서'],
            datasets: [{
                data: [],
                backgroundColor: ['rgb(51,153,255)','rgb(255,255,255)'],//,'rgb(255, 255, 51)', 'rgb(204, 229, 255)'],
                borderColor : 'rgb(150,150,150)',
            }],
        },
        options: {
            responsive: false,
            cutoutPercentage : 50,
            rotation: 1 * Math.PI,
            circumference: 1 * Math.PI
        },
    };
    const config_rain ={
        type: 'doughnut',
        data : {
            labels: ['빗물감지 센서','남은 센서 값'],//['온도센서','습도센서','조도센서', '빗물감지 센서'],
            datasets: [{
                data: [],
                backgroundColor: ['rgb(204, 229, 255)','rgb(255,255,255)'],//,'rgb(255, 255, 51)', 'rgb(204, 229, 255)'],
                borderColor : 'rgb(150,150,150)',
            }],
        },
        options: {
            responsive: false,
            cutoutPercentage : 50,
            rotation: 1 * Math.PI,
            circumference: 1 * Math.PI
        },
    };
    const config_actuator ={
        type: 'horizontalBar',
        data : {
            labels: ['액추에이터 길이'],//['온도센서','습도센서','조도센서', '빗물감지 센서'],
            datasets: [{
                data: [],
                borderWidth:3,
                //axis: 'y',
                label: '액추에이터 길이',
                backgroundColor: ['rgb(128, 128, 128)'],//,'rgb(255, 255, 51)', 'rgb(204, 229, 255)'],
                //borderColor : 'rgb(150,150,150)',
            }],
        },
        options: {
            legend: {
                display: false
            },
            scales: {
                xAxes: [{
                    ticks: {
                        beginAtZero:true,
                        suggestedMax : 50
                    }
                }],
            },
        }
    };
    const context_graph = document.getElementById('canvas').getContext('2d');
    const context_light = document.getElementById('canvas4').getContext('2d');
    const context_temp = document.getElementById('canvas2').getContext('2d');
    const context_humi = document.getElementById('canvas3').getContext('2d');
    const context_rain = document.getElementById('canvas5').getContext('2d'); 
    const context_actuator = document.getElementById('canvas6').getContext('2d'); 

    const lineChart_graph  = new Chart(context_graph , config_graph );
    const lineChart_light = new Chart(context_light, config_light);
    const lineChart_temp = new Chart(context_temp, config_temp);
    const lineChart_humi = new Chart(context_humi, config_humi);
    const lineChart_rain = new Chart(context_rain, config_rain);
    const lineChart_actuator = new Chart(context_actuator, config_actuator);

    const source = new EventSource("/graph")
    const source2 = new EventSource("/other_api")
    
    var first_data_graph = document.getElementById('first_data_graph').innerText.replace(/ /g,"").replace(/\n/g,"").split("/").reverse();
    var arr_data = [];
   
    for(var t=0; t<first_data_graph.length; t++){
        one = first_data_graph[t].substring(10)
        arr_data.push(one.split(","))
    };

    console.log(`확인 : ${arr_data}`);

    for(var b=1; b<30; b++){
        config_graph.data.labels.push(arr_data[b][0]);
        config_graph.data.datasets[0].data.push(arr_data[b][2]);
        config_graph.data.datasets[1].data.push(arr_data[b][1]);
    };

    source.onmessage = function(event) {

        const data_graph = JSON.parse(event.data);
        if (config_graph.data.labels.length === 30) {
            config_graph.data.labels.shift();
            config_graph.data.datasets[0].data.shift();
            config_graph.data.datasets[1].data.shift();
        }
        config_graph.data.labels.push(data_graph.time);
        config_graph.data.datasets[0].data.push(data_graph.value1);
        config_graph.data.datasets[1].data.push(data_graph.value2);

        
        config_light.data.datasets[0].data[0] = data_graph.value3
        config_light.data.datasets[0].data[1] = 1200-data_graph.value3
        
        config_temp.data.datasets[0].data[0] = data_graph.value1
        config_temp.data.datasets[0].data[1] = 50-data_graph.value1
        
        config_humi.data.datasets[0].data[0] = data_graph.value2
        config_humi.data.datasets[0].data[1] = 80-data_graph.value2
         
        config_rain.data.datasets[0].data[0] = data_graph.value4
        config_rain.data.datasets[0].data[1] = 1023-data_graph.value4

        lineChart_graph.update();
        lineChart_light.update();
        lineChart_temp.update();
        lineChart_humi.update();
        lineChart_rain.update();
        
        $("#temp_humi_sensor").text("온도센서 값 : "+data_graph.value1 + " / 습도센서 값: " + data_graph.value2);
        $("#light_sensor").text("조도센서 값 : "+data_graph.value3+" => "+data_graph.value3_1);
        $("#rain_sensor").text("빗물 감지 센서 값 : "+data_graph.value4+" => "+data_graph.value4_1);
        $("#temp_sensor_2").text(data_graph.value1);
        $("#humi_sensor_2").text(data_graph.value2+"%");
        $("#light_sensor_2").text(data_graph.value3);
        $("#rain_sensor_2").text(data_graph.value4);
        $("#water_sensor").text("물탱크 값 : " + data_graph.value5_1);
        $("#water_sensor2").text(data_graph.value5_1);
        //$("#actuator_mm").text(data_graph.value6);

        if(data_graph.value5_1 =="물 부족") {
            $("img#water_level").attr('src',"static/img/red.jpg");
        }
        else {
            $("img#water_level").attr('src',"static/img/green.jpg");
        }
        //C:\Users\home\Desktop\프로젝트\smart_farm_gogo\main\static\picture\2023_02_16_23h13m\output0.jpg
    }
    source2.onmessage = function(event) {
        const data_other = JSON.parse(event.data);
        $("#actuator_cm").text(data_other.value1);
        $("#image").attr("src","static" + data_other.image_path.split('static').slice(-1));
        
        if(data_other.standlight=="ON"){
            $("img#standlight_img").attr('src',"static/img/light_on.png");
        }
        else{
            $("img#standlight_img").attr('src',"static/img/light_off.png");
        }

        //config_actuator.data.datasets[0].data.pop();
        config_actuator.data.datasets[0].data[0] = (data_other.value1.split('.')[0]);
        lineChart_actuator.update();
    }
});

var Target = document.getElementById("clock");

function clock() {
    var time = new Date();

    var month = time.getMonth();
    var date = time.getDate();
    var day = time.getDay();
    var week = ['일', '월', '화', '수', '목', '금', '토'];

    var hours = time.getHours();
    var minutes = time.getMinutes();
    var seconds = time.getSeconds();

    Target.innerText = 
    '현재 시간 : ' +
    `${month + 1}월 ${date}일 ${week[day]}요일 ` +
    `${hours < 10 ? `0${hours}` : hours}:${minutes < 10 ? `0${minutes}` : minutes}:${seconds < 10 ? `0${seconds}` : seconds}`;
        
}
clock();
setInterval(clock, 1000); // 1초마다 실행
