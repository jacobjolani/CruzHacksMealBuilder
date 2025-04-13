document.addEventListener("DOMContentLoaded", () => {
    // 🥗 Nutrition Input Form
    const container = document.createElement("div");
    container.style.display = "flex";
    container.style.flexDirection = "column";
    container.style.alignItems = "center";
    container.style.gap = "15px";
    container.style.marginTop = "30px";
  
    const labels = ["Protein:", "Carbs:", "Calories:", "Fats:"];
    labels.forEach((label) => {
      const wrapper = document.createElement("div");
      wrapper.style.display = "flex";
      wrapper.style.alignItems = "center";
      wrapper.style.gap = "10px";
      wrapper.className = "input-wrapper";
  
      const inputLabel = document.createElement("label");
      inputLabel.textContent = label;
  
      const inputBox = document.createElement("input");
      inputBox.type = "number";
      inputBox.min = "0";
      if (label === "Calories:") {
        inputBox.placeholder = "Enter calories in Kcal";
      }else {
        inputBox.placeholder = `Enter ${label.toLowerCase().replace(":", "")} in grams`;
      }
      inputBox.id = label.toLowerCase().replace(":", "").trim();
  
      wrapper.appendChild(inputLabel);
      wrapper.appendChild(inputBox);
      container.appendChild(wrapper);
    });
  
    const submitButton = document.createElement("button");
    submitButton.textContent = "Submit";
    submitButton.style.marginTop = "20px";

    submitButton.addEventListener("click", () => {
      const inputs = Array.from(container.querySelectorAll("input"));
      const values = inputs.reduce((acc, input) => {
        acc[input.id] = input.value;
        return acc;
      }, {});
  
      // Save data and redirect
      localStorage.setItem("nutritionData", JSON.stringify(values));
      window.location.href = "results.html";
    });
  
    container.appendChild(submitButton);
    document.getElementById("input-container").appendChild(container);
  

  });
  
