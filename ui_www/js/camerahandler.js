

var options = {video: true, audio: true};

var onFail = function(e) {
  alert('Failed to get camera');
  alert(e);
};

var onSuccess = function(stream) {
    var video = document.getElementById('webcam');
    if(navigator.mozGetUserMedia) {
        video.mozSrcObject = stream;
    } else {
        var url = window.URL || window.webkitURL;
        video.src = url.createObjectURL(stream);
    }



};

// Wait 1000 ms before starting the loop
setTimeout( updatevideo ,1000);

function updatevideo() {
    setInterval(updatevideo,30);
    // Make sure the canvas is the same size as the video
    var video = document.getElementById('webcam');
    var canvas = document.getElementById('vcanvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
}

navigator.media.getUserMedia(options, onSuccess, onFail);