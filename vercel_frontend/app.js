const backendUrl =
  window.BACKEND_URL ||
  "https://asesor-financiero-api-wnyk.onrender.com";

const containers = {
  profile: document.querySelector("#profile-fields"),
  history: document.querySelector("#payment-history-fields"),
  bills: document.querySelector("#bill-fields"),
  payments: document.querySelector("#payment-amount-fields"),
};

const form = document.querySelector("#risk-form");
const submitButton = document.querySelector("#submit-button");
const resetButton = document.querySelector("#reset-button");
const statusBox = document.querySelector("#status");
const modelMode = document.querySelector("#model-mode");
const riskMeter = document.querySelector("#risk-meter");
const gaugeValue = document.querySelector("#gauge-value");
const riskLabel = document.querySelector("#risk-label");
const riskCopy = document.querySelector("#risk-copy");
const resultNotes = document.querySelector("#result-notes");
const usageValue = document.querySelector("#usage-value");
const coverageValue = document.querySelector("#coverage-value");
const delayValue = document.querySelector("#delay-value");
const flowTotal = document.querySelector("#flow-total");
const flowChart = document.querySelector("#flow-chart");

const baseSample = {
  LIMIT_BAL: 200000,
  AGE: 34,
  SEX: 2,
  EDUCATION: 2,
  MARRIAGE: 1,
  PAY_0: 1,
  PAY_2: 0,
  PAY_3: 0,
  PAY_4: 0,
  PAY_5: 0,
  PAY_6: 0,
  BILL_AMT1: 125000,
  BILL_AMT2: 120000,
  BILL_AMT3: 118000,
  BILL_AMT4: 111000,
  BILL_AMT5: 95000,
  BILL_AMT6: 90000,
  PAY_AMT1: 4500,
  PAY_AMT2: 5000,
  PAY_AMT3: 4800,
  PAY_AMT4: 5200,
  PAY_AMT5: 5000,
  PAY_AMT6: 4500,
};

const scenarios = {
  balanced: baseSample,
  healthy: {
    ...baseSample,
    LIMIT_BAL: 260000,
    AGE: 38,
    PAY_0: 0,
    PAY_2: 0,
    PAY_3: 0,
    PAY_4: -1,
    PAY_5: -1,
    PAY_6: 0,
    BILL_AMT1: 62000,
    BILL_AMT2: 58000,
    BILL_AMT3: 54000,
    BILL_AMT4: 52000,
    BILL_AMT5: 49000,
    BILL_AMT6: 45000,
    PAY_AMT1: 18000,
    PAY_AMT2: 16000,
    PAY_AMT3: 15000,
    PAY_AMT4: 14500,
    PAY_AMT5: 13000,
    PAY_AMT6: 12500,
  },
  alert: {
    ...baseSample,
    LIMIT_BAL: 90000,
    AGE: 24,
    PAY_0: 3,
    PAY_2: 2,
    PAY_3: 2,
    PAY_4: 1,
    PAY_5: 1,
    PAY_6: 0,
    BILL_AMT1: 87000,
    BILL_AMT2: 85000,
    BILL_AMT3: 82000,
    BILL_AMT4: 78000,
    BILL_AMT5: 76000,
    BILL_AMT6: 72000,
    PAY_AMT1: 800,
    PAY_AMT2: 1000,
    PAY_AMT3: 900,
    PAY_AMT4: 1100,
    PAY_AMT5: 1200,
    PAY_AMT6: 900,
  },
};

const fieldGroups = {
  profile: [
    {
      name: "LIMIT_BAL",
      label: "Credito concedido",
      type: "number",
      min: 1,
      step: 1000,
      hint: "Monto en soles (S/)",
      money: true,
    },
    { name: "AGE", label: "Edad", type: "number", min: 18, max: 100, hint: "18 a 100" },
    {
      name: "SEX",
      label: "Sexo",
      type: "select",
      options: [
        ["1", "Masculino"],
        ["2", "Femenino"],
      ],
    },
    {
      name: "EDUCATION",
      label: "Educacion",
      type: "select",
      options: [
        ["1", "Posgrado"],
        ["2", "Universidad"],
        ["3", "Secundaria"],
        ["4", "Otros"],
      ],
    },
    {
      name: "MARRIAGE",
      label: "Estado civil",
      type: "select",
      options: [
        ["1", "Casado"],
        ["2", "Soltero"],
        ["3", "Otros"],
      ],
    },
  ],
  history: [
    ["PAY_0", "Mes actual"],
    ["PAY_2", "Mes -2"],
    ["PAY_3", "Mes -3"],
    ["PAY_4", "Mes -4"],
    ["PAY_5", "Mes -5"],
    ["PAY_6", "Mes -6"],
  ].map(([name, label]) => ({
    name,
    label,
    type: "number",
    min: -2,
    max: 9,
    step: 1,
    hint: "-2 a 9",
  })),
  bills: [1, 2, 3, 4, 5, 6].map((month) => ({
    name: `BILL_AMT${month}`,
    label: `Saldo ${month}`,
    type: "number",
    min: 0,
    step: 500,
    hint: "S/",
    money: true,
  })),
  payments: [1, 2, 3, 4, 5, 6].map((month) => ({
    name: `PAY_AMT${month}`,
    label: `Pago ${month}`,
    type: "number",
    min: 0,
    step: 500,
    hint: "S/",
    money: true,
  })),
};

function formatMoney(value) {
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);
}

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function createField(config) {
  const field = document.createElement("div");
  field.className = "field";
  if (config.money) field.classList.add("money-field");

  const label = document.createElement("label");
  label.setAttribute("for", config.name);
  label.textContent = config.label;

  const control =
    config.type === "select" ? document.createElement("select") : document.createElement("input");
  control.id = config.name;
  control.name = config.name;

  if (config.type === "select") {
    for (const [value, text] of config.options) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      control.appendChild(option);
    }
  } else {
    control.type = "number";
    if (config.min !== undefined) control.min = config.min;
    if (config.max !== undefined) control.max = config.max;
    if (config.step !== undefined) control.step = config.step;
    control.inputMode = "decimal";
  }

  field.append(label, control);

  if (config.hint) {
    const hint = document.createElement("span");
    hint.textContent = config.hint;
    field.appendChild(hint);
  }

  return field;
}

function renderFields() {
  for (const config of fieldGroups.profile) containers.profile.appendChild(createField(config));
  for (const config of fieldGroups.history) containers.history.appendChild(createField(config));
  for (const config of fieldGroups.bills) containers.bills.appendChild(createField(config));
  for (const config of fieldGroups.payments) containers.payments.appendChild(createField(config));
}

function setPayload(payload) {
  for (const [key, value] of Object.entries(payload)) {
    const input = form.elements[key];
    if (input) input.value = value;
  }
  updateSnapshot();
}

function getPayload() {
  const formData = new FormData(form);
  const payload = {};
  for (const [key, value] of formData.entries()) payload[key] = Number(value);
  return payload;
}

function getSeries(payload, prefix) {
  return [1, 2, 3, 4, 5, 6].map((month) => Number(payload[`${prefix}${month}`]) || 0);
}

function calculateDerived(payload) {
  const bills = getSeries(payload, "BILL_AMT");
  const payments = getSeries(payload, "PAY_AMT");
  const delays = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"].map(
    (key) => Number(payload[key]) || 0,
  );
  const totalBills = bills.reduce((sum, value) => sum + Math.max(value, 0), 0);
  const totalPayments = payments.reduce((sum, value) => sum + Math.max(value, 0), 0);
  const limit = Math.max(Number(payload.LIMIT_BAL) || 1, 1);

  return {
    bills,
    payments,
    usage: Math.min(totalBills / (limit * 6), 2),
    coverage: totalPayments / Math.max(totalBills, 1),
    maxDelay: Math.max(...delays),
    totalBills,
    totalPayments,
  };
}

function drawFlowChart(payload) {
  const { bills, payments } = calculateDerived(payload);
  const maxValue = Math.max(...bills, ...payments, 1);
  const width = 420;
  const height = 132;
  const padding = { top: 10, right: 12, bottom: 24, left: 12 };
  const chartHeight = height - padding.top - padding.bottom;
  const groupWidth = (width - padding.left - padding.right) / 6;
  const barWidth = Math.min(18, groupWidth / 4);
  const parts = [
    `<line class="chart-grid" x1="${padding.left}" y1="${padding.top}" x2="${width - padding.right}" y2="${padding.top}" />`,
    `<line class="chart-grid" x1="${padding.left}" y1="${padding.top + chartHeight / 2}" x2="${width - padding.right}" y2="${padding.top + chartHeight / 2}" />`,
    `<line class="chart-grid" x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" />`,
  ];

  bills.forEach((bill, index) => {
    const x = padding.left + index * groupWidth + groupWidth / 2 - barWidth - 2;
    const payX = padding.left + index * groupWidth + groupWidth / 2 + 2;
    const billHeight = Math.max(2, (Math.max(bill, 0) / maxValue) * chartHeight);
    const payHeight = Math.max(2, (Math.max(payments[index], 0) / maxValue) * chartHeight);
    const billY = padding.top + chartHeight - billHeight;
    const payY = padding.top + chartHeight - payHeight;

    parts.push(`<rect class="bill-bar" x="${x}" y="${billY}" width="${barWidth}" height="${billHeight}" rx="4" />`);
    parts.push(`<rect class="pay-bar" x="${payX}" y="${payY}" width="${barWidth}" height="${payHeight}" rx="4" />`);
    parts.push(`<text class="chart-label" x="${padding.left + index * groupWidth + groupWidth / 2}" y="${height - 6}" text-anchor="middle">M${index + 1}</text>`);
  });

  flowChart.innerHTML = parts.join("");
}

function updateSnapshot() {
  const payload = getPayload();
  const derived = calculateDerived(payload);
  usageValue.textContent = formatPercent(Math.min(derived.usage, 1));
  coverageValue.textContent = formatPercent(derived.coverage);
  delayValue.textContent =
    derived.maxDelay > 0 ? `${derived.maxDelay} ${derived.maxDelay === 1 ? "mes" : "meses"}` : "Sin mora";
  flowTotal.textContent = `${formatMoney(derived.totalBills)} / ${formatMoney(derived.totalPayments)}`;
  drawFlowChart(payload);
}

function setStatus(state, message) {
  statusBox.classList.remove("is-ok", "is-error");
  if (state) statusBox.classList.add(state);
  statusBox.querySelector("span:last-child").textContent = message;
}

function setRiskState(probability, label, data) {
  const percent = Math.round(probability * 100);
  const riskClass =
    probability >= 0.7 ? "risk-high" : probability >= 0.4 ? "risk-medium" : "risk-low";

  riskMeter.classList.remove("risk-low", "risk-medium", "risk-high");
  riskMeter.classList.add(riskClass);
  riskMeter.style.setProperty("--risk-angle", `${Math.min(360, probability * 360)}deg`);
  gaugeValue.textContent = `${percent}%`;
  riskLabel.textContent = `Riesgo ${label}`;
  riskCopy.textContent =
    probability >= 0.7
      ? "Conviene revisar mora y capacidad de pago antes de aprobar."
      : probability >= 0.4
        ? "Perfil intermedio con senales que requieren seguimiento."
        : "Perfil con menor riesgo relativo segun los datos ingresados.";
  modelMode.textContent = `${data.model_name} | ${data.mode}`;

  const notes = data.explanation
    .map((item) => `<li>${item}</li>`)
    .join("");
  resultNotes.innerHTML = `
    <p><strong>Prediccion:</strong> ${data.prediction ? "incumplimiento probable" : "sin incumplimiento probable"} con umbral ${formatPercent(data.threshold)}.</p>
    <ul>${notes}</ul>
  `;
}

async function checkHealth() {
  try {
    const response = await fetch(`${backendUrl}/health`);
    if (!response.ok) throw new Error("health");
    const data = await response.json();
    setStatus("is-ok", `API ${data.status} | ${data.model_mode}`);
  } catch {
    setStatus("is-error", "API no disponible");
  }
}

async function submitPrediction(event) {
  event.preventDefault();
  updateSnapshot();

  submitButton.disabled = true;
  submitButton.textContent = "Calculando...";
  resultNotes.innerHTML = "<p>Procesando perfil financiero...</p>";

  try {
    const response = await fetch(`${backendUrl}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload()),
    });

    if (!response.ok) throw new Error("predict");
    const data = await response.json();
    setRiskState(Number(data.probability), data.risk_label, data);
  } catch {
    riskMeter.classList.remove("risk-low", "risk-medium", "risk-high");
    gaugeValue.textContent = "--";
    riskLabel.textContent = "Sin conexion";
    riskCopy.textContent = "No se pudo consultar la API de Render.";
    modelMode.textContent = "Error";
    resultNotes.innerHTML = "<p>Revisa que el backend de Render este activo y vuelve a intentar.</p>";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Calcular riesgo";
  }
}

function activateScenario(name) {
  document.querySelectorAll(".scenario-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.scenario === name);
  });
  setPayload(scenarios[name]);
}

renderFields();
setPayload(baseSample);
checkHealth();

form.addEventListener("input", updateSnapshot);
form.addEventListener("submit", submitPrediction);
resetButton.addEventListener("click", () => activateScenario("balanced"));

document.querySelectorAll(".scenario-button").forEach((button) => {
  button.addEventListener("click", () => activateScenario(button.dataset.scenario));
});
