const backendUrl =
  window.BACKEND_URL ||
  "https://deploybackend-mu.vercel.app";
const amountFields = document.querySelector("#amount-fields");
const result = document.querySelector("#result");
const statusBox = document.querySelector("#status");

for (const key of [
  "BILL_AMT1",
  "BILL_AMT2",
  "BILL_AMT3",
  "BILL_AMT4",
  "BILL_AMT5",
  "BILL_AMT6",
  "PAY_AMT1",
  "PAY_AMT2",
  "PAY_AMT3",
  "PAY_AMT4",
  "PAY_AMT5",
  "PAY_AMT6",
]) {
  const label = document.createElement("label");
  label.textContent = key;
  const input = document.createElement("input");
  input.name = key;
  input.type = "number";
  input.value = key.startsWith("BILL") ? "90000" : "5000";
  label.appendChild(input);
  amountFields.appendChild(label);
}

async function checkHealth() {
  try {
    const response = await fetch(`${backendUrl}/health`);
    const data = await response.json();
    statusBox.textContent = `API: ${data.status} | modelo: ${data.model_mode}`;
  } catch {
    statusBox.textContent = "API: no disponible";
  }
}

document.querySelector("#risk-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {};
  for (const [key, value] of form.entries()) {
    payload[key] = Number(value);
  }

  result.hidden = false;
  result.textContent = "Calculando...";
  try {
    const response = await fetch(`${backendUrl}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    result.innerHTML = `
      <div class="probability">${(data.probability * 100).toFixed(1)}%</div>
      <strong>Riesgo ${data.risk_label}</strong>
      <p>Modelo: ${data.model_name} (${data.mode})</p>
      <ul>${data.explanation.map((item) => `<li>${item}</li>`).join("")}</ul>
    `;
  } catch (error) {
    result.textContent = "No se pudo conectar con la API. Revisa la URL del backend.";
  }
});

checkHealth();
