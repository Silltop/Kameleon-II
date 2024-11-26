function saveContent(content, endpoint, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", endpoint, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                //console.log("Content saved successfully!");
                if (callback) {
                    callback(null, xhr.responseText);
                }
            } else {
                console.error("Error saving content");
                if (callback) {
                    callback(new Error("Error saving content"), null);
                }
            }
        }
    };
    var data = JSON.stringify({ content: content });
    xhr.send(data);
}

function callEndpoint(endpoint, callback) {
    fetch(endpoint)
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then((rdata) => {
            if (callback) {
                callback(null, rdata);
            }
        })
        .catch((error) => {
            if (callback) {
                callback(error, null);
            }
        });
}

function callAndNotify(endpoint) {
    var alertDiv = document.getElementById("save-status");
    callEndpoint(endpoint, function(err, response) {
        if (err) {
            alertDiv.textContent = err.message; // Display error message
            alertDiv.classList.add("alert-danger");
        } else {
            alertDiv.textContent = response.message; // Display success message
            alertDiv.classList.add("alert-success");
        }
        halfmoon.toastAlert('save-status', 7500);
    });
}

function notifyStatus(type = "error", time = 7500) {
    var alertDiv = document.getElementById("save-status");
    if (type === "error") {
        alertDiv.textContent = "Save error";
        alertDiv.classList.add("alert-danger");
    } else if (type === "success") {
        alertDiv.textContent = "Save success";
        alertDiv.classList.add("alert-success");
    }
    halfmoon.toastAlert('save-status', time);
}