let videoTag = document.getElementById("videoTag");

videoTag.addEventListener("click", async  () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: findAllVideo,
    });
});

function findAllVideo(){
    console.log(document.getElementsByTagName("video"));
}