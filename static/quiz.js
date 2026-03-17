const generateQuizBtn = document.getElementById("generate_quiz");
const quizSection = document.getElementById("quiz_section");
const quizQuestion = document.getElementById("quiz_question");

const labels = [
    document.getElementById("label0"),
    document.getElementById("label1"),
    document.getElementById("label2"),
    document.getElementById("label3")
];

let correctIndex = null;

generateQuizBtn.addEventListener("click", async () => {

    const question = document.getElementById("show_question").innerText;
    const aiAnswer = document.getElementById("response").innerText;

    if (!question || !aiAnswer) {
        alert("Ask a question first before generating a quiz.");
        return;
    }
    // Change button text while loading
    generateQuizBtn.innerText = "Generating question...";
    generateQuizBtn.disabled = true;
    try {

        const response = await fetch("/quiz", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                ai_answer: aiAnswer
            })
        });

        const data = await response.json();

        quizQuestion.innerText = data.question;

        data.options.forEach((option, index) => {
            labels[index].innerText = option;
        });

        correctIndex = data.correct_index;
        // RESET OLD SELECTIONS HERE
        document.querySelectorAll('input[name="quiz_option"]').forEach(r => r.checked = false);

        // Remove previous result text
        document.getElementById("quiz_result").innerText = "";

        quizSection.hidden = false;

    } catch (error) {

        console.error(error);
        alert("Failed to generate quiz.");

    } finally {

        // Restore button text
        generateQuizBtn.innerText = "Generate Quiz";
        generateQuizBtn.disabled = false;

    }

});

const submitQuizBtn = document.getElementById("submit_quiz");
const resultText = document.getElementById("quiz_result");

submitQuizBtn.addEventListener("click", () => {

    const selected = document.querySelector('input[name="quiz_option"]:checked');

    if (!selected) {
        resultText.innerText = "Please select an option.";
        return;
    }

    const selectedIndex = Number(selected.value);

    if (selectedIndex === correctIndex) {

        resultText.innerText = "Correct!";

    } else {

        const correctLabel = document.getElementById("label" + correctIndex).innerText;

        resultText.innerText = "Incorrect. Correct answer: " + correctLabel;

    }

});
