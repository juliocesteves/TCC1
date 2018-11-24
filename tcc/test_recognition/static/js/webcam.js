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
        }, function (stream) {
            var video = document.getElementsByTagName('video')[0];

            video.src = window.URL.createObjectURL(stream);
            recordRTC = RecordRTC(stream, options);
            showWebCamStream();
        }, function (e) {
            window.alert('Please enable your webcam to begin recording');
        });
    } else {
        window.alert('Your browser does not support recording, try Google Chrome');
    }
}

function accessWebCam() {
    init();

    setInterval(doJob, 20);

    setInterval(doJobCollectNames, 2000);
}


function login() {
    window.location.href = "http://localhost:5000/proc_frame_view";
}

function doJobCollectNames() {
    $.ajax({
        type: "GET",
        url: "/get_reconhecidos",
    }).done(function (request) {
        const newList = request.split('\n');

        $("#names_container").html("");
        for (let index = 0; index < newList.length; index++) {
            const element = newList[index];
            $("#names_container").append(element + "<br />");
        }
    });
}

function doJob() {
    sendWebcamPhoto();
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

function showWebCamStream() {
    //  
    $("#video_container").fadeIn();
}

function hideWebCamStream() {
    $("#video_container").fadeOut();
}

function sendWebcamPhoto() {

    var context = canvas.getContext('2d');
    //photo.style.setProperty('display', 'block');

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    var data = canvas.toDataURL('image/png');
    //photo.setAttribute('src', data);

    $.ajax({
        type: "POST",
        url: "/process_frame",
        data: {
            imageBase64: data,
            'csrfmiddlewaretoken': $("input[name='csrfmiddlewaretoken']").val()
        }
    }).done(function (request) {

        var obj = JSON.parse(request);
        photo.setAttribute('src', 'data:image/png;base64,' + obj.image);

        //canvas.setAttribute('src', 'data:image/png;base64,' + x.image);


        //context.drawImage(x.image, 0, 0, canvas.width, canvas.height);
    });

}
