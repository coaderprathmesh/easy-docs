const questionInput = document.getElementById("question");
const show_question = document.getElementById("show_question");
const askButton = document.getElementById("ask");
const responseBox = document.getElementById("response");

async function sendQuestion() {

    const question = questionInput.value.trim();

    questionInput.value = "";

    if (!question) {
        responseBox.innerText = "Please enter a question.";
        return;
    }

    responseBox.innerText = "Thinking...";

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_query: question
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        show_question.innerText = ` you asked: ${question}`;


        responseBox.innerText = data.answer;

    } catch (error) {

        console.error(error);
        responseBox.innerText = "Error while processing your request.";

    }
}

askButton.addEventListener("click", sendQuestion);

questionInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendQuestion();
    }
});