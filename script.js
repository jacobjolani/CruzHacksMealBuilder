alert("JavaScript is running!");

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("input-container");

  const form = document.createElement("form");
  form.id = "meal-form";

  const inputs = [
    { id: "protein", label: "Protein (g)" },
    { id: "calories", label: "Calories" },
    { id: "fats", label: "Fats (g)" },
    { id: "carbs", label: "Carbs (g)" },
  ];

  inputs.forEach((input) => {
    const inputWrapper = document.createElement("div");
    inputWrapper.classList.add("input-wrapper");

    const label = document.createElement("label");
    label.textContent = input.label;
    label.setAttribute("for", input.id);

    const inputField = document.createElement("input");
    inputField.type = "number";
    inputField.id = input.id;
    inputField.name = input.id;

    inputWrapper.appendChild(label);
    inputWrapper.appendChild(inputField);
    form.appendChild(inputWrapper);
  });

  container.appendChild(form);

  const submitButton = document.createElement("button");
  submitButton.textContent = "Submit";
  container.appendChild(submitButton);

  submitButton.addEventListener("click", () => {
    const inputFields = Array.from(form.querySelectorAll("input"));
    const values = inputFields.reduce((acc, input) => {
      acc[input.id] = input.value;
      return acc;
    }, {});

    fetch('/generate_meal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        goal: Object.keys(values).find(key => values[key] != ""),
        target_amount: Object.values(values).find(value => value != ""),
      }),
    })
      .then(response => response.json())
      .then(data => {
        sessionStorage.setItem('apiResults', JSON.stringify(data));
        window.location.href = "results.html";
      })
      .catch(error => {
        console.error('Error:', error);
      });
  });
});