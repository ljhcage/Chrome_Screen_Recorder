'use strict'

var player = $("#player")[0];
var recordPlayer = $("#recordPlayer")[0];
var recordBtn = $("#recordBtn");
var playBtn = $("#playBtn");
var downloadBtn = $("#downloadBtn");

var buffer; // 用于存储录制数据（数组）
var mediaStream;
var mediaRecoder;


jQuery.support.cors = true;

start();

// 录制按钮点击事件
recordBtn.click(function(){
    // console.log(recordBtn.text());
    if (recordBtn.text()==='开始录制') {
        startRecord();
        recordBtn.text('停止录制');
        playBtn.attr('disabled',false);
        downloadBtn.attr('disabled',false);
    }else if (recordBtn.text()==='停止录制') {
        stopRecord();
        recordBtn.text('开始录制');
        // playBtn.attr('disabled',true);
        // downloadBtn.attr('disabled',true);
    }
});

// 播放按钮点击事件
playBtn.click(function(){
    var blob = new Blob(buffer,{type:'video/mp4'});
    // 根据缓存数据生成url给recordPlayer进行播放
    recordPlayer.src = window.URL.createObjectURL(blob);
    recordPlayer.srcObject = null;
    recordPlayer.controls = true; // 显示播放控件
});

// 下载按钮点击事件
downloadBtn.click(function(){
    var blob = new Blob(buffer,{type:'video/mp4'});
    // 根据缓存数据生成url
    var url = window.URL.createObjectURL(blob);
    // 创建一个a标签，通过a标签指向url来下载
    var a = document.createElement('a');
    a.href = url;
    a.style.display = 'none'; // 不显示a标签
    a.download = 'test.webm'; // 下载的文件名
    a.click(); // 调用a标签的点击事件进行下载
});

// 开始录制
function startRecord(){
    var options = {ignoreMutedMedia:true,audioBitsPerSecond: 128000,videoBitsPerSecond: 2500000,mimeType:'video/webm'};
    if(!MediaRecorder.isTypeSupported(options.mimeType)){
        console.log('不支持'+options.mimeType);
        return;
    }

    try{
        buffer = [];
        mediaRecoder = new MediaRecorder(mediaStream,options);
    }catch(e){
        console.log('创建MediaRecorder失败!');
        return;
    }
    mediaRecoder.ondataavailable = handleDataAvailable;
    // 开始录制，设置录制时间片为10ms(每10s触发一次ondataavilable事件)
    mediaRecoder.start(1000);
}

// 停止录制
function stopRecord (){
    mediaRecoder.stop();
}

// 触发ondataavilable事件的回调函数
function handleDataAvailable(e){
    if (e && e.data && e.data.size>0) {
        buffer.push(e.data);
    }
    console.log(buffer.length)
    if(buffer.length>0){
        console.log("upload start")
        var blob = new Blob(buffer,{type:'video/mp4'});
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "recoder");
        xhr.overrideMimeType("application/octet-stream");
        xhr.send(blob);
        xhr.onreadystatechange = function (e) {
            if (xhr.readyState === 4) {
             if (xhr.status === 200) {
                buffer.length = 0;
              }
             }
            }
    }
}

function start(){
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        console.log('不支采集音视频数据！');
    }else{
        // 采集音频数据
        var constrants = {
            video:true,
            audio:true
        };
        navigator.mediaDevices.getDisplayMedia(constrants).then(gotMediaStream).catch(handleError);
    }
}


// 采集音频数据成功时调用的方法
function gotMediaStream(stream){
    mediaStream = stream;
    player.srcObject = stream;
}

// 采集音频数据失败时调用的方法
function handleError(err){
    console.log(err.name+':'+err.message);
}