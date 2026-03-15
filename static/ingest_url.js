const urlInput = document.getElementById("url");
const sendUrlButton = document.getElementById("send_url");
const webStatus = document.getElementById("web_chunk");

async function sendURL() {

    const url = urlInput.value.trim();

    if (!url) {
        webStatus.innerText = "Please enter a URL.";
        return;
    }

    webStatus.innerText = "Fetching and processing website...";

    try {

        const response = await fetch("/ingest-url", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        if (!response.ok) {
            throw new Error("Server error while processing URL.");
        }

        const result = await response.json();

        webStatus.innerText = result.response;

    } catch (error) {

        console.error(error);
        webStatus.innerText = "Error while ingesting website.";

    }
}

sendUrlButton.addEventListener("click", sendURL);