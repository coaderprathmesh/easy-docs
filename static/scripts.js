const ingestButton = document.getElementById("ingest");
const fileInput = document.getElementById("documents");
const statusText = document.getElementById("chunk_count");

ingestButton.addEventListener("click", async () => {

    const files = fileInput.files;

    if (!files.length) {
        statusText.innerText = "Please select at least one file.";
        return;
    }

    const formData = new FormData();

    for (let file of files) {
        formData.append("files", file);
    }

    statusText.innerText = "Uploading and processing documents...";

    ingestButton.disabled = true;
    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error while processing files.");
        }

        const result = await response.json();

        statusText.innerText = result.response;

    } catch (error) {

        console.error(error);
        statusText.innerText = "Error: Failed to upload or process files.";

    } finally {

        ingestButton.disabled = false;

    }

});