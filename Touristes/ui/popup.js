var videoTag = document.getElementById("videoTag");
var getCurrentFrame = document.getElementById("getCurrentFrame")
var videos;

videoTag.addEventListener("click", async  () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: findAllVideo,
    });
});

getCurrentFrame.addEventListener("click", async  () => {
    console.log(captureVideo(videos[0]));
});


function findAllVideo(){
    videos = document.getElementsByTagName("video");
    var canvas = document.createElement("canvas");
    canvas.width = videos[1].videoWidth;
    canvas.height = videos[1].videoHeight;
    var canvasContext = canvas.getContext("2d");
    canvasContext.drawImage(videos[1], 0, 0);
    console.log(canvas.toDataURL('image/png'));
    console.log(videos)
}

