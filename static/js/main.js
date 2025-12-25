document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("predictionForm");
  const resultDiv = document.getElementById("result");
  const errorDiv = document.getElementById("error");
  const submitBtn = form.querySelector('button[type="submit"]');
  const btnText = submitBtn.querySelector(".btn-text");
  const btnLoader = submitBtn.querySelector(".btn-loader");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    // Hide previous results/errors
    resultDiv.classList.add("d-none");
    errorDiv.classList.add("d-none");

    // Show loading state
    submitBtn.disabled = true;
    btnText.classList.add("d-none");
    btnLoader.classList.remove("d-none");

    try {
      // Collect form data
      const formData = new FormData(form);

      // Make prediction request
      const response = await fetch("/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        displayResult(data);
      } else {
        displayError(data.error || "An error occurred during prediction.");
      }
    } catch (error) {
      console.error("Error:", error);
      displayError("Network error. Please try again.");
    } finally {
      // Reset button state
      submitBtn.disabled = false;
      btnText.classList.remove("d-none");
      btnLoader.classList.add("d-none");
    }
  });

  function displayResult(data) {
    // Set risk level
    const riskLevel = document.querySelector(".risk-level");
    const riskText = document.querySelector(".risk-text");

    if (data.prediction === 1) {
      riskLevel.className = "risk-level high";
      riskLevel.innerHTML = "⚠️";
      riskText.textContent = "High Risk";
      riskText.style.color = "#e74c3c";
    } else {
      riskLevel.className = "risk-level low";
      riskLevel.innerHTML = "✓";
      riskText.textContent = "Low Risk";
      riskText.style.color = "#27ae60";
    }

    // Set probability bars
    const probNoDisease = (data.probability_no_disease * 100).toFixed(1);
    const probDisease = (data.probability_disease * 100).toFixed(1);

    document.getElementById("prob-no-disease").style.width =
      probNoDisease + "%";
    document.getElementById("prob-no-value").textContent = probNoDisease + "%";

    document.getElementById("prob-disease").style.width = probDisease + "%";
    document.getElementById("prob-disease-value").textContent =
      probDisease + "%";

    // Show result
    resultDiv.classList.remove("d-none");

    // Smooth scroll to result
    setTimeout(() => {
      resultDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }

  function displayError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove("d-none");

    // Smooth scroll to error
    setTimeout(() => {
      errorDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }

  // Add input validation
  const numberInputs = form.querySelectorAll('input[type="number"]');
  numberInputs.forEach((input) => {
    input.addEventListener("input", function () {
      const value = parseFloat(this.value);
      const min = parseFloat(this.min);
      const max = parseFloat(this.max);

      if (this.value && (value < min || value > max)) {
        this.setCustomValidity(`Value must be between ${min} and ${max}`);
      } else {
        this.setCustomValidity("");
      }
    });
  });

  // Add some sample data for testing
  if (window.location.search.includes("demo=true")) {
    fillDemoData();
  }

  function fillDemoData() {
    // Sample patient data
    const demoData = {
      age: 63,
      sex: 1,
      cp: 3,
      trestbps: 145,
      chol: 233,
      fbs: 1,
      restecg: 0,
      thalach: 150,
      exang: 0,
      oldpeak: 2.3,
      slope: 0,
      ca: 0,
      thal: 1,
    };

    Object.keys(demoData).forEach((key) => {
      const input = form.querySelector(`[name="${key}"]`);
      if (input) {
        input.value = demoData[key];
      }
    });
  }

  // Add clear form functionality
  const clearBtn = document.createElement("button");
  clearBtn.type = "button";
  clearBtn.className = "btn btn-outline-secondary mt-2";
  clearBtn.textContent = "Clear Form";
  clearBtn.addEventListener("click", function () {
    form.reset();
    resultDiv.classList.add("d-none");
    errorDiv.classList.add("d-none");
  });

  form.appendChild(clearBtn);
});
