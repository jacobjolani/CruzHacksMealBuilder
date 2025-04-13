document.addEventListener("DOMContentLoaded", () => {
    // ... (Your existing form creation code) ...

    submitButton.addEventListener("click", () => {
        const inputs = Array.from(container.querySelectorAll("input"));
        const values = inputs.reduce((acc, input) => {
            acc[input.id] = input.value;
            return acc;
        }, {});

        // Send data to the backend API
        fetch('/meal_plan', { // Adjust the URL to match your backend
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goal: values.goal, // Assuming you have input fields with ids goal, target_amount
                target_amount: parseFloat(values.target_amount),
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error); // Display error message
            } else {
                // Display the meal plan results on your webpage
                displayResults(data); // Create a function to display the results
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        });
    });

    // ... (Your AI assistant code) ...
});

function displayResults(data) {
    const resultDiv = document.getElementById("results"); // Assuming you have a div with id results in result.html
    resultDiv.innerHTML = `<h2>Heres your Generated Meal Plan</h2>`;
    for (const item of data.meal_plan) {
        resultDiv.innerHTML += `<p>${item}</p>`;
    }
    resultDiv.innerHTML += `<p>Total Calories: ${data.total_nutrition.calories}g</p>`;
    resultDiv.innerHTML += `<p>Total Fat: ${data.total_nutrition.fat}g</p>`;
    resultDiv.innerHTML += `<p>Total Carbs: ${data.total_nutrition.carbs}g</p>`;
    resultDiv.innerHTML += `<p>Total Protein: ${data.total_nutrition.protein}g</p>`;

    window.location.href = "results.html";

}