
function addRegexSetting() {
    let settingsList = document.getElementById("regex-settings");

    regexSettings = document.getElementsByClassName("text-input-small");

    //Loop through inputs and set the attribute value to the text so we can later copy the elements properly
    for (let i = 0; i < regexSettings.length; i++) {
        inputTag = regexSettings[i];
        inputTag.setAttribute("value", inputTag.value);
    }

    //Get the template, set its display to default, add it to the settingsList, make the templates display none again
    let template = document.getElementById("regex-setting-template");
    template.style.display = "";
    settingsList.innerHTML = template.outerHTML + settingsList.innerHTML;
    template.style.display = "none";
}

function removeRegexSetting(regexSetting) {
    regexSetting.outerHTML = "";
}

function saveRegex() {
    //TODO: Finish
    regexSettings = document.getElementsByClassName("text-input-small");
    regexTextList = "";

    //Offset by one because of the hidden template
    for (let i = 0; i < regexSettings.length-1; i++) {
        regexText = regexSettings[i+1].value;
        regexTextList += regexText + "\n";
    }

    let XHR = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('regex-filters', regexTextList);

    XHR.addEventListener('load', function (event) {
        if (XHR.status == 200) {
            console.log(XHR.response);
        }
        else {
            console.log('Follow query failed to send.');
        }
    });

    XHR.open('POST', '/regex');

    XHR.send(formData);
    //Send text list to the server
}