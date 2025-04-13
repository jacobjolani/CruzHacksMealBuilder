document.addEventListener("DOMContentLoaded", () => {
  // ... (input form creation) ...

  submitButton.addEventListener("click", () => {
      const inputs = Array.from(container.querySelectorAll("input"));
      const values = inputs.reduce((acc, input) => {
          acc[input.id] = input.value;
          return acc;
      }, {});

      // Send data to the Flask API
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

  // ... (rest of the script) ...
});