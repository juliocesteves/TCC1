var video = document.getElementsByTagName('video')[0],
    recordRTC = null,
    videoURL = '',
    canvas = document.getElementById('my_canvas'),
    options = {
        type: 'video',
        video: {
            width: 320,
            height: 240
        },
        canvas: {
            width: 320,
            height: 240
        }
    };

function init() {
    try {
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
    } catch (e) {
        window.alert('Your browser does not support WebVideo, try Google Chrome');
    }
    if (navigator.getUserMedia) {
        navigator.getUserMedia({
            video: true
        }, function(stream) {
            console.log('stream', stream);
            video.src = window.URL.createObjectURL(stream);
            recordRTC = RecordRTC(stream, options);
            showWebCamStream();
        }, function(e) {
            window.alert('Please enable your webcam to begin recording');
        });
    } else {
        window.alert('Your browser does not support recording, try Google Chrome');
    }
}

function record() {
    clearphoto();
    recordRTC.startRecording();
    $("#record").attr("style", "color: red;");
}

function stop() {
    recordRTC.stopRecording(function(url) {
        videoURL = url;
        $("input[name='video_url']").val(videoURL);
    });
    $("#record").attr("style", "color: black;");
}

function load() {
    video.src = videoURL;
}

function accessWebCam() {
    init();
}

function takepicture() {
//    canvas.style.removeProperty('display');
    var context = canvas.getContext('2d');
    photo.style.setProperty('display', 'block');

    canvas.width = video.width;
    canvas.height = video.height;
    context.drawImage(video, 0, 0, video.width, video.height);
//    debugger;
    var data = canvas.toDataURL('image/png');
    photo.setAttribute('src', data);
    video.style.setProperty('display', 'none');
}

function clearphoto() {
    video.style.removeProperty('display');
    var context = canvas.getContext('2d');
    context.fillStyle = "#AAA";
    context.fillRect(0, 0, canvas.width, canvas.height);

    var data = canvas.toDataURL('image/png');
    photo.setAttribute('src', '');
    photo.style.setProperty('display', 'none');
    canvas.style.setProperty('display', 'none');
}

document.onkeypress = function(evt) {
    evt = evt || window.event;
    var charCode = evt.keyCode || evt.which;
    var charStr = String.fromCharCode(charCode);
    if (charStr == "w" && typeof(recordRTC) != "undefined") {
        stop();
        recordRTC = undefined;
        hideWebCamStream();
    } else if (charStr == "r") {
        record();
    } else if (charStr == "s") {
        stop();
    } else if (charStr == "l") {
        load();
    }
};

function showWebCamStream() {
    // debugger;
    $("#video_container").fadeIn();
}

function hideWebCamStream() {
    $("#video_container").fadeOut();
}

$('#myform').submit(function() {
    showLoadingScreen();

    if ($("input[name='video_url']").val() != "") {
        sendWebcamVideo();
        $("input[name='video_url']").val("");
        return false;
        // debugger;
    }

    else if (photo.src != '') {
        sendWebcamPhoto();
        $("input[name='video_url']").val("");
        return false;
    }

    return true; // return false to cancel form action
});


function sendWebcamPhoto() {

    $.ajax({
        type: "POST",
        url: window.location.href + "_json",
        data:{
            imageBase64: photo.src,
            'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
        }
        }).done(function(request) {
        console.log('sent');
        new_data = request;
        loadCharts(new_data);
        hideLoadingScreen();
    });

}

function sendWebcamVideo() {
    var fileType = 'video'; // or "audio"
    var fileName = 'ABCDEF.webm';  // or "wav"

    var formData = new FormData();
    formData.append(fileType + '-filename', fileName);
    formData.append('file', recordRTC.getBlob());
    formData.append('num_frames', $('input[name="num_frames"').val());
    formData.append("csrfmiddlewaretoken", $("input[name='csrfmiddlewaretoken']").val())

    xhr(window.location.href + "_json" , formData, function (fName) {
        window.open(location.href + fName);
    });

    function xhr(url, data, callback) {
        var request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            console.log(request);
            if (request.readyState == 4 && request.status == 200) {
                new_data = request.responseText;
                data = JSON.parse(new_data);
                loadCharts(data);
                hideLoadingScreen();
            }
        };
        request.open('POST', url);
        request.send(data, function(e) {
            console.log(e);
        });
    }
}
