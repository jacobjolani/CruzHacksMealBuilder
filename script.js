document.addEventListener("DOMContentLoaded", () => {
    const container = document.createElement("div");
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.gap = "10px";

    const labels = ["Protein:", "Carbs:", "Calories:", "Fats:"];
    labels.forEach(label => {
        const wrapper = document.createElement("div");

        const inputLabel = document.createElement("label");
        inputLabel.textContent = label;
        inputLabel.style.marginRight = "10px";

        const inputBox = document.createElement("input");
        inputBox.type = "text";
        inputBox.placeholder = `Enter ${label.toLowerCase()}`;
        inputBox.id = label.toLowerCase().replace(":", "").trim(); // Fix the ID

        wrapper.appendChild(inputLabel);
        wrapper.appendChild(inputBox);
        container.appendChild(wrapper);
    });

    // ✅ Create and append submit button inside the DOMContentLoaded block
    const submitButton = document.createElement("button");
    submitButton.textContent = "Submit";
    submitButton.style.marginTop = "10px";

    submitButton.addEventListener("click", () => {
        const inputs = Array.from(container.querySelectorAll("input"));
        const values = inputs.reduce((acc, input) => {
            acc[input.id] = input.value;
            return acc;
        }, {});
        console.log("Submitted values:", values);
    });

    container.appendChild(submitButton);
    document.body.appendChild(container);
});
