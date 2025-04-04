function sendData() {
    let code = document.getElementById("codeInput").value;
    fetch("/submit", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "code=" + encodeURIComponent(code)
    }).then(response => response.text())
      .then(data => console.log(data));
}