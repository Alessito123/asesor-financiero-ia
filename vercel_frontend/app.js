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
const previewReportButton = document.querySelector("#preview-report-button");
const reportPreview = document.querySelector("#program-report-preview");
const reportFrame = document.querySelector("#program-report-frame");
const reportStatus = document.querySelector("#report-status");
const reportButtons = document.querySelectorAll("[data-report-format]");
const languageToggle = document.querySelector("#language-toggle");
const themeToggle = document.querySelector("#theme-toggle");
const refreshStatsButton = document.querySelector("#refresh-stats-button");
const productionModel = document.querySelector("#production-model");
const modelGrid = document.querySelector("#model-grid");
const statsTableBody = document.querySelector("#stats-table-body");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const chatPanel = document.querySelector("#chatbot");
const chatLauncher = document.querySelector("#chat-launcher");
const chatClose = document.querySelector("#chat-close");
const toastStack = document.querySelector("#toast-stack");
const navLinks = document.querySelectorAll('.ghost-link[href^="#"]');
const profileNameInput = document.querySelector("#profile-name-input");
const saveProfileButton = document.querySelector("#save-profile-button");
const profileList = document.querySelector("#profile-list");
const profileCount = document.querySelector("#profile-count");
const restoreLastButton = document.querySelector("#restore-last-button");
const compareScenario = document.querySelector("#compare-scenario");
const runCompareButton = document.querySelector("#run-compare-button");
const compareGrid = document.querySelector("#compare-grid");
const predictionHistory = document.querySelector("#prediction-history");
const clearHistoryButton = document.querySelector("#clear-history-button");
const fullscreenReportButton = document.querySelector("#fullscreen-report-button");
const onboarding = document.querySelector("#onboarding");
const onboardingStart = document.querySelector("#onboarding-start");
const wizardSteps = document.querySelectorAll("[data-step]");
const wizardSections = document.querySelectorAll("[data-wizard-step]");
const wizardPrev = document.querySelector("#wizard-prev");
const wizardNext = document.querySelector("#wizard-next");
const driversList = document.querySelector("#drivers-list");

let currentLanguage = localStorage.getItem("afi_language") || "es";
let currentTheme = localStorage.getItem("afi_theme") || "light";
let reportPreviewUrl = null;
let latestStats = null;
let lastPrediction = null;
let isSubmitting = false;
let currentWizardStep = 0;
let statusState = { state: null, key: "api_connecting", params: {} };
let reportState = { key: "report_ready", isError: false, params: {} };
let predictionHistoryItems = readStoredArray("afi_prediction_history").slice(0, 3);

const translations = {
  es: {
    brand_subtitle: "Riesgo crediticio personal",
    api_connecting: "Conectando API",
    api_ok: "API {status} | {mode}",
    api_unavailable: "API no disponible",
    nav_models: "Modelos",
    nav_reports: "Reportes",
    nav_chat: "Chatbot",
    theme_dark: "Oscuro",
    theme_light: "Claro",
    overview_eyebrow: "FastAPI + IA financiera",
    page_title: "Evalua el riesgo de incumplimiento con datos de credito.",
    metric_backend: "Backend",
    metric_frontend: "Frontend",
    simulator_eyebrow: "Simulador",
    client_profile: "Perfil del cliente",
    reset: "Restablecer",
    currency_note: "Todos los montos monetarios se ingresan en soles peruanos (S/).",
    scenario_current: "Perfil actual",
    scenario_healthy: "Cliente estable",
    scenario_alert: "Mora elevada",
    personal_data: "Datos personales",
    payment_history: "Historial de pago",
    billed_balances: "Saldos facturados en S/",
    payments_done: "Pagos realizados en S/",
    calculate_risk: "Calcular riesgo",
    calculating: "Calculando...",
    result_eyebrow: "Resultado",
    model_reading: "Lectura del modelo",
    no_calculation: "Sin calculo",
    waiting_data: "Esperando datos",
    waiting_copy: "Completa el perfil y ejecuta la prediccion.",
    model_explanation_pending: "La explicacion del modelo aparecera aqui despues de calcular.",
    avg_usage: "Uso promedio",
    coverage: "Pago / saldo",
    max_delay: "Mora maxima",
    no_delay: "Sin mora",
    month: "mes",
    months: "meses",
    balances_vs_payments: "Saldos vs pagos",
    risk_low: "Riesgo bajo",
    risk_medium: "Riesgo medio",
    risk_high: "Riesgo alto",
    risk_low_copy: "Perfil con menor riesgo relativo segun los datos ingresados.",
    risk_medium_copy: "Perfil intermedio con senales que requieren seguimiento.",
    risk_high_copy: "Conviene revisar mora y capacidad de pago antes de aprobar.",
    prediction: "Prediccion",
    probable_default: "incumplimiento probable",
    no_probable_default: "sin incumplimiento probable",
    with_threshold: "con umbral",
    processing_profile: "Procesando perfil financiero...",
    no_connection: "Sin conexion",
    render_connection_error: "No se pudo consultar la API de Render.",
    check_backend: "Revisa que el backend de Render este activo y vuelve a intentar.",
    models_eyebrow: "Validacion IA",
    models_title: "Modelos neuronales y pruebas estadisticas",
    refresh_stats: "Actualizar pruebas",
    production_model: "Modelo en produccion",
    classic_models: "Modelos clasicos",
    hybrid_models: "Modelos hibridos",
    table_model: "Modelo",
    table_time: "Tiempo",
    table_validation: "Validacion",
    stats_loading: "Cargando pruebas estadisticas...",
    stats_error: "No se pudo cargar la validacion estadistica.",
    selected_model: "Modelo seleccionado como mejor resultado.",
    no_interpretation: "Sin comparacion estadistica disponible.",
    model_type_classic: "Clasico",
    model_type_hybrid: "Hibrido",
    auc_label: "AUC",
    f1_label: "F1",
    process_time: "Tiempo de proceso",
    significant_both: "Diferencia significativa en t-test y Wilcoxon.",
    significant_t: "Diferencia significativa en t-test pareado.",
    significant_w: "Diferencia significativa en Wilcoxon.",
    not_significant: "Sin evidencia robusta al 5%.",
    program_eyebrow: "Programa",
    financial_report_title: "Reporte del analisis financiero",
    preview_pdf: "Previsualizar PDF",
    preview: "Vista previa",
    financial_report: "Reporte financiero",
    no_report: "Sin reporte generado",
    no_report_hint: "Calcula el riesgo o previsualiza el PDF con los datos actuales.",
    pdf_report_desc: "Resultado, indicadores y recomendaciones.",
    editable_report: "Reporte editable",
    docx_report_desc: "Word generado desde la prediccion actual.",
    analysis_table: "Tabla del analisis",
    xlsx_report_desc: "Excel con resultado, indicadores y variables.",
    report_ready: "Listo para generar con los datos del formulario.",
    report_generating_preview: "Generando vista previa del reporte...",
    report_preparing_download: "Preparando descarga...",
    report_preview_ready: "Vista previa generada con los datos actuales.",
    report_downloaded: "Reporte descargado con los datos actuales.",
    report_error: "No se pudo generar el reporte. Revisa la conexion con Render.",
    api_error_detail: "Render respondio con un error de validacion.",
    report_stale: "Datos modificados. Genera nuevamente el reporte para actualizarlo.",
    academic_docs: "Documentos academicos del proyecto",
    chat_eyebrow: "Asistente",
    chat_title: "Chatbot del asesor financiero",
    chat_mode: "Soporte academico",
    chat_launcher: "Asistente IA",
    chat_close: "Cerrar",
    chat_welcome: "Hola, puedo explicar el modelo LSTM, los 5 modelos entrenados, reportes y pruebas estadisticas.",
    chat_placeholder: "Pregunta sobre modelos, reportes o riesgo",
    chat_error: "No pude responder ahora. Revisa la conexion con Render.",
    chat_typing: "Consultando al asistente...",
    send: "Enviar",
    saved_profiles: "Perfiles guardados",
    save_profile: "Guardar perfil",
    profile_name: "Nombre del perfil",
    profile_saved: "Perfil guardado",
    load_profile: "Cargar",
    delete_profile: "Eliminar",
    no_profiles: "Aun no hay perfiles guardados.",
    profile_limit: "Se guardan hasta 5 perfiles recientes.",
    validation_error: "Revisa los campos marcados antes de calcular.",
    compare_title: "Comparador de escenarios",
    compare_button: "Comparar",
    compare_hint: "Calcula el riesgo y compara el perfil actual contra un escenario alternativo.",
    current_profile: "Perfil actual",
    compared_profile: "Escenario comparado",
    compare_loading: "Calculando comparacion...",
    compare_error: "No se pudo comparar escenarios.",
    history_title: "Historial de la sesion",
    clear_history: "Limpiar",
    no_history: "Aun no hay predicciones en esta sesion.",
    reload_profile: "Usar perfil",
    restore_last: "Restaurar ultima evaluacion",
    restored_last: "Ultima evaluacion restaurada",
    fullscreen_report: "Ampliar",
    toast_dismiss: "Cerrar aviso",
    wizard_step_profile: "Perfil",
    wizard_step_history: "Historial",
    wizard_step_payments: "Pagos",
    wizard_prev: "Anterior",
    wizard_next: "Siguiente",
    drivers_title: "Factores explicativos",
    drivers_method: "XAI operativo",
    drivers_hint: "Calcula el riesgo para ver que variables empujan o reducen el resultado.",
    driver_increases: "Aumenta riesgo",
    driver_reduces: "Reduce riesgo",
    driver_delay: "Mora reciente",
    driver_delay_desc: "{value} meses de atraso maximo detectado.",
    driver_coverage: "Cobertura de pagos",
    driver_coverage_desc: "Pago acumulado de {value} frente a saldos.",
    driver_usage: "Uso de credito",
    driver_usage_desc: "Uso promedio de {value} del limite disponible.",
    driver_limit: "Capacidad aprobada",
    driver_limit_desc: "Limite de credito de {value}.",
    driver_age: "Madurez financiera",
    driver_age_desc: "Edad registrada: {value} anos.",
    driver_no_signals: "El perfil no muestra factores extremos; se mantiene como riesgo bajo relativo.",
    onboarding_eyebrow: "Inicio rapido",
    onboarding_title: "Evalua riesgo financiero con IA en minutos",
    onboarding_copy: "Ingresa o carga un perfil, calcula el riesgo, compara escenarios y descarga reportes del programa en PDF, Word o Excel.",
    onboarding_start: "Comenzar",
  },
  en: {
    brand_subtitle: "Personal credit risk",
    api_connecting: "Connecting API",
    api_ok: "API {status} | {mode}",
    api_unavailable: "API unavailable",
    nav_models: "Models",
    nav_reports: "Reports",
    nav_chat: "Chatbot",
    theme_dark: "Dark",
    theme_light: "Light",
    overview_eyebrow: "FastAPI + financial AI",
    page_title: "Evaluate default risk with credit profile data.",
    metric_backend: "Backend",
    metric_frontend: "Frontend",
    simulator_eyebrow: "Simulator",
    client_profile: "Client profile",
    reset: "Reset",
    currency_note: "All monetary values are entered in Peruvian soles (S/).",
    scenario_current: "Current profile",
    scenario_healthy: "Stable client",
    scenario_alert: "High delay",
    personal_data: "Personal data",
    payment_history: "Payment history",
    billed_balances: "Billed balances in S/",
    payments_done: "Payments made in S/",
    calculate_risk: "Calculate risk",
    calculating: "Calculating...",
    result_eyebrow: "Result",
    model_reading: "Model reading",
    no_calculation: "No calculation",
    waiting_data: "Waiting for data",
    waiting_copy: "Complete the profile and run the prediction.",
    model_explanation_pending: "The model explanation will appear here after calculation.",
    avg_usage: "Average usage",
    coverage: "Payment / balance",
    max_delay: "Max delay",
    no_delay: "No delay",
    month: "month",
    months: "months",
    balances_vs_payments: "Balances vs payments",
    risk_low: "Low risk",
    risk_medium: "Medium risk",
    risk_high: "High risk",
    risk_low_copy: "Lower relative risk profile based on the entered data.",
    risk_medium_copy: "Intermediate profile with signals that need monitoring.",
    risk_high_copy: "Review payment capacity and late payments before approval.",
    prediction: "Prediction",
    probable_default: "probable default",
    no_probable_default: "no probable default",
    with_threshold: "with threshold",
    processing_profile: "Processing financial profile...",
    no_connection: "No connection",
    render_connection_error: "Could not query the Render API.",
    check_backend: "Check that the Render backend is active and try again.",
    models_eyebrow: "AI validation",
    models_title: "Neural models and statistical tests",
    refresh_stats: "Refresh tests",
    production_model: "Production model",
    classic_models: "Classic models",
    hybrid_models: "Hybrid models",
    table_model: "Model",
    table_time: "Time",
    table_validation: "Validation",
    stats_loading: "Loading statistical tests...",
    stats_error: "Could not load statistical validation.",
    selected_model: "Selected as the best model.",
    no_interpretation: "No statistical comparison available.",
    model_type_classic: "Classic",
    model_type_hybrid: "Hybrid",
    auc_label: "AUC",
    f1_label: "F1",
    process_time: "Process time",
    significant_both: "Significant difference in t-test and Wilcoxon.",
    significant_t: "Significant difference in paired t-test.",
    significant_w: "Significant difference in Wilcoxon.",
    not_significant: "No robust evidence at 5%.",
    program_eyebrow: "Program",
    financial_report_title: "Financial analysis report",
    preview_pdf: "Preview PDF",
    preview: "Preview",
    financial_report: "Financial report",
    no_report: "No report generated",
    no_report_hint: "Calculate risk or preview the PDF with the current data.",
    pdf_report_desc: "Result, indicators and recommendations.",
    editable_report: "Editable report",
    docx_report_desc: "Word generated from the current prediction.",
    analysis_table: "Analysis table",
    xlsx_report_desc: "Excel with result, indicators and variables.",
    report_ready: "Ready to generate with the form data.",
    report_generating_preview: "Generating report preview...",
    report_preparing_download: "Preparing download...",
    report_preview_ready: "Preview generated with current data.",
    report_downloaded: "Report downloaded with current data.",
    report_error: "Could not generate the report. Check the Render connection.",
    api_error_detail: "Render returned a validation error.",
    report_stale: "Data changed. Generate the report again to update it.",
    academic_docs: "Academic project documents",
    chat_eyebrow: "Assistant",
    chat_title: "Financial advisor chatbot",
    chat_mode: "Academic support",
    chat_launcher: "AI Assistant",
    chat_close: "Close",
    chat_welcome: "Hi, I can explain the LSTM model, the 5 trained models, reports and statistical tests.",
    chat_placeholder: "Ask about models, reports or risk",
    chat_error: "I could not answer now. Check the Render connection.",
    chat_typing: "Asking the assistant...",
    send: "Send",
    saved_profiles: "Saved profiles",
    save_profile: "Save profile",
    profile_name: "Profile name",
    profile_saved: "Profile saved",
    load_profile: "Load",
    delete_profile: "Delete",
    no_profiles: "No saved profiles yet.",
    profile_limit: "Up to 5 recent profiles are saved.",
    validation_error: "Check the marked fields before calculating.",
    compare_title: "Scenario comparison",
    compare_button: "Compare",
    compare_hint: "Calculate risk and compare the current profile against an alternative scenario.",
    current_profile: "Current profile",
    compared_profile: "Compared scenario",
    compare_loading: "Calculating comparison...",
    compare_error: "Could not compare scenarios.",
    history_title: "Session history",
    clear_history: "Clear",
    no_history: "No predictions in this session yet.",
    reload_profile: "Use profile",
    restore_last: "Restore last evaluation",
    restored_last: "Last evaluation restored",
    fullscreen_report: "Expand",
    toast_dismiss: "Dismiss notice",
    wizard_step_profile: "Profile",
    wizard_step_history: "History",
    wizard_step_payments: "Payments",
    wizard_prev: "Previous",
    wizard_next: "Next",
    drivers_title: "Explanatory factors",
    drivers_method: "Operational XAI",
    drivers_hint: "Calculate risk to see which variables push or reduce the result.",
    driver_increases: "Increases risk",
    driver_reduces: "Reduces risk",
    driver_delay: "Recent delay",
    driver_delay_desc: "{value} months of maximum delay detected.",
    driver_coverage: "Payment coverage",
    driver_coverage_desc: "Accumulated payment of {value} against balances.",
    driver_usage: "Credit usage",
    driver_usage_desc: "Average usage of {value} of the available limit.",
    driver_limit: "Approved capacity",
    driver_limit_desc: "Credit limit of {value}.",
    driver_age: "Financial maturity",
    driver_age_desc: "Registered age: {value} years.",
    driver_no_signals: "The profile does not show extreme factors; it remains a relatively low risk case.",
    onboarding_eyebrow: "Quick start",
    onboarding_title: "Evaluate financial risk with AI in minutes",
    onboarding_copy: "Enter or load a profile, calculate risk, compare scenarios and download program reports as PDF, Word or Excel.",
    onboarding_start: "Start",
  },
};

const fieldLanguage = {
  es: {
    labels: {
      LIMIT_BAL: "Credito concedido",
      AGE: "Edad",
      SEX: "Sexo",
      EDUCATION: "Educacion",
      MARRIAGE: "Estado civil",
      PAY_0: "Mes actual",
      PAY_2: "Mes -2",
      PAY_3: "Mes -3",
      PAY_4: "Mes -4",
      PAY_5: "Mes -5",
      PAY_6: "Mes -6",
      BILL_AMT1: "Saldo 1",
      BILL_AMT2: "Saldo 2",
      BILL_AMT3: "Saldo 3",
      BILL_AMT4: "Saldo 4",
      BILL_AMT5: "Saldo 5",
      BILL_AMT6: "Saldo 6",
      PAY_AMT1: "Pago 1",
      PAY_AMT2: "Pago 2",
      PAY_AMT3: "Pago 3",
      PAY_AMT4: "Pago 4",
      PAY_AMT5: "Pago 5",
      PAY_AMT6: "Pago 6",
    },
    hints: {
      LIMIT_BAL: "Monto en soles (S/)",
      AGE: "18 a 100",
      PAY_0: "-2 a 9",
      PAY_2: "-2 a 9",
      PAY_3: "-2 a 9",
      PAY_4: "-2 a 9",
      PAY_5: "-2 a 9",
      PAY_6: "-2 a 9",
      BILL_AMT1: "S/",
      BILL_AMT2: "S/",
      BILL_AMT3: "S/",
      BILL_AMT4: "S/",
      BILL_AMT5: "S/",
      BILL_AMT6: "S/",
      PAY_AMT1: "S/",
      PAY_AMT2: "S/",
      PAY_AMT3: "S/",
      PAY_AMT4: "S/",
      PAY_AMT5: "S/",
      PAY_AMT6: "S/",
    },
    options: {
      SEX: { 1: "Masculino", 2: "Femenino" },
      EDUCATION: { 1: "Posgrado", 2: "Universidad", 3: "Secundaria", 4: "Otros" },
      MARRIAGE: { 1: "Casado", 2: "Soltero", 3: "Otros" },
    },
  },
  en: {
    labels: {
      LIMIT_BAL: "Granted credit",
      AGE: "Age",
      SEX: "Sex",
      EDUCATION: "Education",
      MARRIAGE: "Marital status",
      PAY_0: "Current month",
      PAY_2: "Month -2",
      PAY_3: "Month -3",
      PAY_4: "Month -4",
      PAY_5: "Month -5",
      PAY_6: "Month -6",
      BILL_AMT1: "Balance 1",
      BILL_AMT2: "Balance 2",
      BILL_AMT3: "Balance 3",
      BILL_AMT4: "Balance 4",
      BILL_AMT5: "Balance 5",
      BILL_AMT6: "Balance 6",
      PAY_AMT1: "Payment 1",
      PAY_AMT2: "Payment 2",
      PAY_AMT3: "Payment 3",
      PAY_AMT4: "Payment 4",
      PAY_AMT5: "Payment 5",
      PAY_AMT6: "Payment 6",
    },
    hints: {
      LIMIT_BAL: "Amount in soles (S/)",
      AGE: "18 to 100",
      PAY_0: "-2 to 9",
      PAY_2: "-2 to 9",
      PAY_3: "-2 to 9",
      PAY_4: "-2 to 9",
      PAY_5: "-2 to 9",
      PAY_6: "-2 to 9",
      BILL_AMT1: "S/",
      BILL_AMT2: "S/",
      BILL_AMT3: "S/",
      BILL_AMT4: "S/",
      BILL_AMT5: "S/",
      BILL_AMT6: "S/",
      PAY_AMT1: "S/",
      PAY_AMT2: "S/",
      PAY_AMT3: "S/",
      PAY_AMT4: "S/",
      PAY_AMT5: "S/",
      PAY_AMT6: "S/",
    },
    options: {
      SEX: { 1: "Male", 2: "Female" },
      EDUCATION: { 1: "Graduate", 2: "University", 3: "High school", 4: "Other" },
      MARRIAGE: { 1: "Married", 2: "Single", 3: "Other" },
    },
  },
};

const explanationTranslations = {
  "Existe historial de pago atrasado en al menos un mes.": "There is late payment history in at least one month.",
  "La utilizacion promedio del credito es elevada.": "Average credit utilization is high.",
  "El perfil se ubica en zona de menor riesgo relativo.": "The profile is in a lower relative risk zone.",
};

function readStoredArray(key) {
  try {
    const value = JSON.parse(localStorage.getItem(key) || "[]");
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

function writeStoredArray(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showToast(message, type = "info") {
  if (!toastStack) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${escapeHtml(message)}</span>
    <button type="button" aria-label="${t("toast_dismiss")}">x</button>
  `;
  toastStack.appendChild(toast);
  const remove = () => {
    toast.classList.add("is-leaving");
    window.setTimeout(() => toast.remove(), 220);
  };
  toast.querySelector("button").addEventListener("click", remove);
  window.setTimeout(remove, 5200);
}

function apiErrorMessage(data) {
  if (!data) return t("api_error_detail");
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail.length) {
    const first = data.detail[0];
    const field = Array.isArray(first.loc) ? first.loc.at(-1) : "";
    return `${field ? `${field}: ` : ""}${first.msg || t("api_error_detail")}`;
  }
  return t("api_error_detail");
}

async function readErrorMessage(response) {
  try {
    return apiErrorMessage(await response.json());
  } catch {
    return t("api_error_detail");
  }
}

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

function t(key, params = {}) {
  const template = translations[currentLanguage][key] || translations.es[key] || key;
  return Object.entries(params).reduce(
    (text, [name, value]) => text.replaceAll(`{${name}}`, value),
    template,
  );
}

function formatMoney(value) {
  const locale = currentLanguage === "en" ? "en-US" : "es-PE";
  return `S/ ${new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(Number(value) || 0)}`;
}

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function formatDecimal(value, digits = 3) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "--";
  return number.toFixed(digits);
}

function reportFilename(format) {
  const stamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, "");
  return `reporte_financiero_programa_${stamp}.${format}`;
}

function applyTheme() {
  document.documentElement.dataset.theme = currentTheme;
  themeToggle.textContent = t(currentTheme === "dark" ? "theme_light" : "theme_dark");
}

function applyFieldLanguage() {
  const language = fieldLanguage[currentLanguage];
  document.querySelectorAll("[data-field-label]").forEach((label) => {
    const fieldName = label.dataset.fieldLabel;
    label.textContent = language.labels[fieldName] || label.textContent;
  });
  document.querySelectorAll("[data-field-hint]").forEach((hint) => {
    const fieldName = hint.dataset.fieldHint;
    hint.textContent = language.hints[fieldName] || hint.textContent;
  });
  document.querySelectorAll("[data-field-option]").forEach((option) => {
    const [fieldName, optionValue] = option.dataset.fieldOption.split(":");
    option.textContent = language.options[fieldName]?.[optionValue] || option.textContent;
  });
}

function applyLanguage() {
  document.documentElement.lang = currentLanguage;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });
  languageToggle.textContent = currentLanguage === "es" ? "EN" : "ES";
  applyTheme();
  applyFieldLanguage();
  setStatus(statusState.state, t(statusState.key, statusState.params));
  setReportStatus(t(reportState.key, reportState.params), reportState.isError);
  updateSnapshot();
  renderRiskState();
  renderStatistics();
  renderProfiles();
  renderPredictionHistory();
  renderCompareHint();
  updateWizard();
  if (!lastPrediction) {
    modelMode.textContent = t("no_calculation");
    riskLabel.textContent = t("waiting_data");
    riskCopy.textContent = t("waiting_copy");
    resultNotes.innerHTML = `<p>${t("model_explanation_pending")}</p>`;
    renderDriverHint();
  }
  if (!isSubmitting) submitButton.textContent = t("calculate_risk");
}

function setReportStatus(message, isError = false) {
  reportStatus.textContent = message;
  reportStatus.classList.toggle("is-error", isError);
}

function setReportStatusKey(key, isError = false, params = {}) {
  reportState = { key, isError, params };
  setReportStatus(t(key, params), isError);
}

function setReportButtonsLoading(isLoading) {
  previewReportButton.disabled = isLoading;
  reportButtons.forEach((button) => {
    button.disabled = isLoading;
  });
}

function setStatus(state, message) {
  statusBox.classList.remove("is-ok", "is-error");
  if (state) statusBox.classList.add(state);
  statusBox.querySelector("span:last-child").textContent = message;
}

function setStatusKey(state, key, params = {}) {
  statusState = { state, key, params };
  setStatus(state, t(key, params));
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function fetchProgramReport(format, { preview = false } = {}) {
  setReportButtonsLoading(true);
  setReportStatusKey(preview ? "report_generating_preview" : "report_preparing_download");

  try {
    const response = await fetch(`${backendUrl}/reports/financial/${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload()),
    });

    if (!response.ok) throw new Error(await readErrorMessage(response));
    const blob = await response.blob();

    if (preview) {
      if (reportPreviewUrl) URL.revokeObjectURL(reportPreviewUrl);
      reportPreviewUrl = URL.createObjectURL(blob);
      reportFrame.src = reportPreviewUrl;
      reportPreview.classList.add("has-document");
      setReportStatusKey("report_preview_ready");
      showToast(t("report_preview_ready"), "success");
    } else {
      downloadBlob(blob, reportFilename(format));
      setReportStatusKey("report_downloaded");
      showToast(t("report_downloaded"), "success");
    }
  } catch (error) {
    setReportStatusKey("report_error", true);
    showToast(error.message || t("report_error"), "error");
  } finally {
    setReportButtonsLoading(false);
  }
}

function createField(config) {
  const field = document.createElement("div");
  field.className = "field";
  if (config.money) field.classList.add("money-field");

  const label = document.createElement("label");
  label.setAttribute("for", config.name);
  label.dataset.fieldLabel = config.name;
  label.textContent = config.label;

  const control =
    config.type === "select" ? document.createElement("select") : document.createElement("input");
  control.id = config.name;
  control.name = config.name;
  control.dataset.fieldName = config.name;

  if (config.type === "select") {
    for (const [value, text] of config.options) {
      const option = document.createElement("option");
      option.value = value;
      option.dataset.fieldOption = `${config.name}:${value}`;
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

  control.addEventListener("input", () => validateField(control));
  control.addEventListener("blur", () => validateField(control));

  field.append(label, control);

  if (config.hint) {
    const hint = document.createElement("span");
    hint.dataset.fieldHint = config.name;
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
  Array.from(form.querySelectorAll("input, select")).forEach(validateField);
}

function getSavedProfiles() {
  return readStoredArray("afi_profiles");
}

function saveCurrentProfile() {
  const name = (profileNameInput.value || "").trim() || `${t("current_profile")} ${new Date().toLocaleTimeString()}`;
  const existing = getSavedProfiles().filter((profile) => profile.name !== name);
  const nextProfiles = [
    {
      name,
      createdAt: new Date().toISOString(),
      payload: getPayload(),
    },
    ...existing,
  ].slice(0, 5);
  writeStoredArray("afi_profiles", nextProfiles);
  profileNameInput.value = "";
  setReportStatus(`${t("profile_saved")}: ${name}`);
  showToast(`${t("profile_saved")}: ${name}`, "success");
  renderProfiles();
}

function renderProfiles() {
  if (!profileList || !profileCount) return;
  const profiles = getSavedProfiles();
  profileCount.textContent = profiles.length;

  if (!profiles.length) {
    profileList.innerHTML = `<p class="muted">${t("no_profiles")} ${t("profile_limit")}</p>`;
    return;
  }

  profileList.innerHTML = profiles
    .map((profile, index) => {
      const safeName = escapeHtml(profile.name);
      return `
        <div class="profile-item" data-profile-index="${index}">
          <div>
            <span>${new Date(profile.createdAt).toLocaleDateString()}</span>
            <strong>${safeName}</strong>
          </div>
          <div class="profile-item-actions">
            <button class="secondary-button small" type="button" data-profile-action="load">${t("load_profile")}</button>
            <button class="secondary-button small" type="button" data-profile-action="delete">${t("delete_profile")}</button>
          </div>
        </div>
      `;
    })
    .join("");
}

function handleProfileAction(event) {
  const button = event.target.closest("[data-profile-action]");
  if (!button) return;
  const item = button.closest("[data-profile-index]");
  const index = Number(item?.dataset.profileIndex);
  const profiles = getSavedProfiles();
  const profile = profiles[index];
  if (!profile) return;

  if (button.dataset.profileAction === "load") {
    setPayload(profile.payload);
    setReportStatusKey("report_stale");
  } else {
    writeStoredArray(
      "afi_profiles",
      profiles.filter((_, candidateIndex) => candidateIndex !== index),
    );
    renderProfiles();
  }
}

function getPayload() {
  const formData = new FormData(form);
  const payload = {};
  for (const [key, value] of formData.entries()) payload[key] = Number(value);
  return payload;
}

function validateField(control) {
  if (!control || control.disabled) return true;
  let isValid = true;
  const value = control.value;

  if (control.tagName === "INPUT" && control.type === "number") {
    const numeric = Number(value);
    const min = control.min === "" ? null : Number(control.min);
    const max = control.max === "" ? null : Number(control.max);
    isValid = value !== "" && Number.isFinite(numeric);
    if (isValid && min !== null) isValid = numeric >= min;
    if (isValid && max !== null) isValid = numeric <= max;
  }

  control.classList.toggle("is-error", !isValid);
  control.classList.toggle("is-valid", isValid && value !== "");
  control.setAttribute("aria-invalid", String(!isValid));
  return isValid;
}

function validateForm() {
  const controls = Array.from(form.querySelectorAll("input, select"));
  const results = controls.map(validateField);
  return results.every(Boolean);
}

function getWizardControls(step) {
  return Array.from(form.querySelectorAll(`[data-wizard-step="${step}"] input, [data-wizard-step="${step}"] select`));
}

function validateWizardStep(step) {
  const controls = getWizardControls(step);
  return controls.map(validateField).every(Boolean);
}

function updateWizard() {
  if (!wizardSteps.length || !wizardSections.length) return;
  wizardSections.forEach((section) => {
    section.hidden = Number(section.dataset.wizardStep) !== currentWizardStep;
  });
  wizardSteps.forEach((button) => {
    const step = Number(button.dataset.step);
    const isActive = step === currentWizardStep;
    button.classList.toggle("is-active", isActive);
    button.classList.toggle("is-done", step < currentWizardStep);
    button.setAttribute("aria-current", isActive ? "step" : "false");
  });
  wizardPrev.disabled = currentWizardStep === 0;
  wizardNext.hidden = currentWizardStep === 2;
  submitButton.hidden = currentWizardStep !== 2;
}

function goToWizardStep(step, options = {}) {
  const nextStep = Math.max(0, Math.min(2, Number(step)));
  if (options.validateCurrent && nextStep > currentWizardStep && !validateWizardStep(currentWizardStep)) {
    resultNotes.innerHTML = `<p>${t("validation_error")}</p>`;
    showToast(t("validation_error"), "error");
    return;
  }
  currentWizardStep = nextStep;
  updateWizard();
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

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function buildRiskDrivers(payload) {
  const derived = calculateDerived(payload);
  const limit = Number(payload.LIMIT_BAL) || 0;
  const age = Number(payload.AGE) || 0;
  const drivers = [];

  if (derived.maxDelay > 0) {
    drivers.push({
      labelKey: "driver_delay",
      descriptionKey: "driver_delay_desc",
      direction: "increase",
      impact: clamp(0.05 + derived.maxDelay * 0.055, 0.05, 0.32),
      params: { value: derived.maxDelay },
    });
  }

  if (derived.coverage < 0.08) {
    drivers.push({
      labelKey: "driver_coverage",
      descriptionKey: "driver_coverage_desc",
      direction: "increase",
      impact: clamp(0.14 - derived.coverage, 0.06, 0.18),
      params: { value: formatPercent(derived.coverage) },
    });
  } else if (derived.coverage > 0.18) {
    drivers.push({
      labelKey: "driver_coverage",
      descriptionKey: "driver_coverage_desc",
      direction: "reduce",
      impact: clamp(derived.coverage * 0.34, 0.06, 0.18),
      params: { value: formatPercent(derived.coverage) },
    });
  }

  if (derived.usage > 0.65) {
    drivers.push({
      labelKey: "driver_usage",
      descriptionKey: "driver_usage_desc",
      direction: "increase",
      impact: clamp((derived.usage - 0.55) * 0.22, 0.05, 0.20),
      params: { value: formatPercent(derived.usage) },
    });
  } else if (derived.usage < 0.25) {
    drivers.push({
      labelKey: "driver_usage",
      descriptionKey: "driver_usage_desc",
      direction: "reduce",
      impact: clamp((0.3 - derived.usage) * 0.28, 0.04, 0.12),
      params: { value: formatPercent(derived.usage) },
    });
  }

  if (limit >= 250000) {
    drivers.push({
      labelKey: "driver_limit",
      descriptionKey: "driver_limit_desc",
      direction: "reduce",
      impact: 0.07,
      params: { value: formatMoney(limit) },
    });
  } else if (limit > 0 && limit < 80000) {
    drivers.push({
      labelKey: "driver_limit",
      descriptionKey: "driver_limit_desc",
      direction: "increase",
      impact: 0.06,
      params: { value: formatMoney(limit) },
    });
  }

  if (age > 0 && age < 25) {
    drivers.push({
      labelKey: "driver_age",
      descriptionKey: "driver_age_desc",
      direction: "increase",
      impact: 0.04,
      params: { value: age },
    });
  } else if (age >= 45) {
    drivers.push({
      labelKey: "driver_age",
      descriptionKey: "driver_age_desc",
      direction: "reduce",
      impact: 0.04,
      params: { value: age },
    });
  }

  return drivers.sort((a, b) => b.impact - a.impact).slice(0, 5);
}

function renderDriverHint() {
  if (!driversList) return;
  driversList.innerHTML = `<div class="compare-empty">${t("drivers_hint")}</div>`;
}

function renderRiskDrivers(payload) {
  if (!driversList) return;
  if (!payload) {
    renderDriverHint();
    return;
  }

  const drivers = buildRiskDrivers(payload);
  if (!drivers.length) {
    driversList.innerHTML = `<div class="compare-empty">${t("driver_no_signals")}</div>`;
    return;
  }

  driversList.innerHTML = drivers
    .map((driver) => {
      const isRisk = driver.direction === "increase";
      const width = Math.round(clamp((driver.impact / 0.32) * 100, 16, 100));
      return `
        <article class="driver-item ${isRisk ? "is-risk" : "is-protective"}">
          <div class="driver-main">
            <div>
              <span>${t(isRisk ? "driver_increases" : "driver_reduces")}</span>
              <strong>${t(driver.labelKey)}</strong>
            </div>
            <b>${isRisk ? "+" : "-"}${formatPercent(driver.impact)}</b>
          </div>
          <div class="driver-bar" aria-hidden="true">
            <i style="width: ${width}%"></i>
          </div>
          <p>${t(driver.descriptionKey, driver.params)}</p>
        </article>
      `;
    })
    .join("");
}

function buildChatPredictionContext() {
  if (!lastPrediction?.payload) return null;
  const { probability, data, payload } = lastPrediction;
  return {
    probability,
    risk_label: t(riskLabelKey(probability)),
    model_name: data.model_name,
    mode: data.mode,
    threshold: data.threshold,
    prediction: data.prediction,
    indicators: calculateDerived(payload),
    drivers: buildRiskDrivers(payload).map((driver) => ({
      factor: t(driver.labelKey),
      direction: driver.direction,
      impact: driver.impact,
      detail: t(driver.descriptionKey, driver.params),
    })),
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
    derived.maxDelay > 0
      ? `${derived.maxDelay} ${derived.maxDelay === 1 ? t("month") : t("months")}`
      : t("no_delay");
  flowTotal.textContent = `${formatMoney(derived.totalBills)} / ${formatMoney(derived.totalPayments)}`;
  drawFlowChart(payload);
}

function riskLabelKey(probability) {
  if (probability >= 0.7) return "risk_high";
  if (probability >= 0.4) return "risk_medium";
  return "risk_low";
}

function riskCopyKey(probability) {
  if (probability >= 0.7) return "risk_high_copy";
  if (probability >= 0.4) return "risk_medium_copy";
  return "risk_low_copy";
}

function renderRiskState() {
  if (!lastPrediction) return;
  const { probability, data, payload } = lastPrediction;
  const percent = Math.round(probability * 100);
  const riskClass =
    probability >= 0.7 ? "risk-high" : probability >= 0.4 ? "risk-medium" : "risk-low";

  riskMeter.classList.remove("risk-low", "risk-medium", "risk-high");
  riskMeter.classList.add(riskClass);
  riskMeter.style.setProperty("--risk-angle", `${Math.min(360, probability * 360)}deg`);
  gaugeValue.textContent = `${percent}%`;
  riskLabel.textContent = t(riskLabelKey(probability));
  riskCopy.textContent = t(riskCopyKey(probability));
  modelMode.textContent = `${data.model_name} | ${data.mode}`;

  const notes = (data.explanation || [])
    .map((item) => (currentLanguage === "en" ? explanationTranslations[item] || item : item))
    .map((item) => `<li>${item}</li>`)
    .join("");
  resultNotes.innerHTML = `
    <p><strong>${t("prediction")}:</strong> ${
      data.prediction ? t("probable_default") : t("no_probable_default")
    } ${t("with_threshold")} ${formatPercent(data.threshold)}.</p>
    <ul>${notes}</ul>
  `;
  renderRiskDrivers(payload);
}

function setRiskState(probability, label, data, payload) {
  lastPrediction = { probability, label, data, payload };
  renderRiskState();
}

function addPredictionHistory(payload, data) {
  predictionHistoryItems = [
    {
      createdAt: new Date().toISOString(),
      probability: Number(data.probability),
      modelName: data.model_name,
      mode: data.mode,
      threshold: data.threshold,
      prediction: data.prediction,
      explanation: data.explanation || [],
      payload,
    },
    ...predictionHistoryItems,
  ].slice(0, 3);
  writeStoredArray("afi_prediction_history", predictionHistoryItems);
  renderPredictionHistory();
}

function renderPredictionHistory() {
  if (!predictionHistory) return;
  if (restoreLastButton) restoreLastButton.hidden = predictionHistoryItems.length === 0;
  if (!predictionHistoryItems.length) {
    predictionHistory.innerHTML = `<p class="muted">${t("no_history")}</p>`;
    return;
  }

  predictionHistory.innerHTML = predictionHistoryItems
    .map((item, index) => {
      const probability = Number(item.probability) || 0;
      return `
        <div class="history-item" data-history-index="${index}">
          <div>
            <span>${new Date(item.createdAt).toLocaleTimeString()}</span>
            <strong>${formatPercent(probability)} - ${t(riskLabelKey(probability))}</strong>
          </div>
          <button class="secondary-button small" type="button" data-history-action="load">${t("reload_profile")}</button>
        </div>
      `;
    })
    .join("");
}

function handleHistoryAction(event) {
  const button = event.target.closest("[data-history-action]");
  if (!button) return;
  const item = button.closest("[data-history-index]");
  const historyItem = predictionHistoryItems[Number(item?.dataset.historyIndex)];
  if (!historyItem) return;
  restoreHistoryItem(historyItem);
}

function restoreHistoryItem(historyItem) {
  if (!historyItem) return;
  setPayload(historyItem.payload);
  const probability = Number(historyItem.probability) || 0;
  setRiskState(
    probability,
    riskLabelKey(probability),
    {
      probability,
      model_name: historyItem.modelName || "LSTM",
      mode: historyItem.mode || "trained",
      threshold: historyItem.threshold ?? 0.5,
      prediction: historyItem.prediction ?? Number(probability >= 0.5),
      explanation: historyItem.explanation || [],
    },
    historyItem.payload,
  );
  setReportStatusKey("report_stale");
  showToast(t("restored_last"), "success");
}

function restoreLastEvaluation() {
  restoreHistoryItem(predictionHistoryItems[0]);
}

function clearPredictionHistory() {
  predictionHistoryItems = [];
  writeStoredArray("afi_prediction_history", predictionHistoryItems);
  renderPredictionHistory();
}

async function checkHealth() {
  try {
    const response = await fetch(`${backendUrl}/health`);
    if (!response.ok) throw new Error("health");
    const data = await response.json();
    setStatusKey("is-ok", "api_ok", { status: data.status, mode: data.model_mode });
  } catch {
    setStatusKey("is-error", "api_unavailable");
  }
}

async function submitPrediction(event) {
  event.preventDefault();
  if (isSubmitting) return;
  if (currentWizardStep < 2) {
    goToWizardStep(currentWizardStep + 1, { validateCurrent: true });
    return;
  }
  updateSnapshot();
  if (!validateForm()) {
    resultNotes.innerHTML = `<p>${t("validation_error")}</p>`;
    showToast(t("validation_error"), "error");
    return;
  }
  const payload = getPayload();

  isSubmitting = true;
  submitButton.disabled = true;
  submitButton.textContent = t("calculating");
  resultNotes.innerHTML = `<p>${t("processing_profile")}</p>`;

  try {
    const response = await fetch(`${backendUrl}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error(await readErrorMessage(response));
    const data = await response.json();
    setRiskState(Number(data.probability), data.risk_label, data, payload);
    addPredictionHistory(payload, data);
    fetchProgramReport("pdf", { preview: true });
  } catch (error) {
    lastPrediction = null;
    riskMeter.classList.remove("risk-low", "risk-medium", "risk-high");
    gaugeValue.textContent = "--";
    riskLabel.textContent = t("no_connection");
    riskCopy.textContent = error.message || t("render_connection_error");
    modelMode.textContent = "Error";
    resultNotes.innerHTML = `<p>${error.message || t("check_backend")}</p>`;
    renderDriverHint();
    showToast(error.message || t("check_backend"), "error");
  } finally {
    isSubmitting = false;
    submitButton.disabled = false;
    submitButton.textContent = t("calculate_risk");
  }
}

function activateScenario(name) {
  document.querySelectorAll(".scenario-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.scenario === name);
  });
  setPayload(scenarios[name]);
}

function renderCompareHint() {
  if (!compareGrid || compareGrid.dataset.hasResult === "true") return;
  compareGrid.innerHTML = `<div class="compare-empty">${t("compare_hint")}</div>`;
}

async function predictPayload(payload) {
  const response = await fetch(`${backendUrl}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("predict");
  return response.json();
}

function compareCard(title, result, payload) {
  const probability = Number(result.probability) || 0;
  const derived = calculateDerived(payload);
  return `
    <article class="compare-card ${probability >= 0.7 ? "risk-high" : probability >= 0.4 ? "risk-medium" : "risk-low"}">
      <span>${title}</span>
      <strong>${formatPercent(probability)}</strong>
      <p>${t(riskLabelKey(probability))} | ${t("coverage")}: ${formatPercent(derived.coverage)} | ${t("max_delay")}: ${
        derived.maxDelay > 0 ? `${derived.maxDelay}` : t("no_delay")
      }</p>
    </article>
  `;
}

async function runScenarioComparison() {
  if (!validateForm()) {
    compareGrid.dataset.hasResult = "true";
    compareGrid.innerHTML = `<div class="compare-empty">${t("validation_error")}</div>`;
    return;
  }

  compareGrid.dataset.hasResult = "true";
  compareGrid.innerHTML = `
    <div class="skeleton-card"></div>
    <div class="skeleton-card"></div>
  `;
  runCompareButton.disabled = true;

  try {
    const currentPayload = getPayload();
    const selectedScenario = compareScenario.value;
    const alternativePayload = scenarios[selectedScenario] || scenarios.healthy;
    const currentResult = await predictPayload(currentPayload);
    const alternativeResult = await predictPayload(alternativePayload);
    compareGrid.innerHTML = [
      compareCard(t("current_profile"), currentResult, currentPayload),
      compareCard(t("compared_profile"), alternativeResult, alternativePayload),
    ].join("");
  } catch {
    compareGrid.innerHTML = `<div class="compare-empty">${t("compare_error")}</div>`;
  } finally {
    runCompareButton.disabled = false;
  }
}

function modelTypeLabel(model) {
  const rawType = currentLanguage === "en" ? model.type_en : model.type;
  return rawType === "hybrid" || rawType === "hibrido" ? t("model_type_hybrid") : t("model_type_classic");
}

function validationSummary(test) {
  if (!test) return t("no_interpretation");
  const tP = Number(test.paired_t_pvalue);
  const wP = Number(test.wilcoxon_pvalue);
  const tSig = Number.isFinite(tP) && tP < 0.05;
  const wSig = Number.isFinite(wP) && wP < 0.05;

  if (currentLanguage === "es" && test.interpretation) return test.interpretation;
  if (tSig && wSig) return `${t("significant_both")} t=${formatDecimal(tP)}, W=${formatDecimal(wP)}.`;
  if (tSig) return `${t("significant_t")} t=${formatDecimal(tP)}, W=${formatDecimal(wP)}.`;
  if (wSig) return `${t("significant_w")} t=${formatDecimal(tP)}, W=${formatDecimal(wP)}.`;
  return `${t("not_significant")} t=${formatDecimal(tP)}, W=${formatDecimal(wP)}.`;
}

function renderStatistics() {
  if (!modelGrid || !statsTableBody) return;
  if (!latestStats) return;

  const comparison = latestStats.comparison || [];
  const tests = latestStats.statistical_tests || [];
  const comparisonByModel = new Map(comparison.map((row) => [row.model, row]));
  const testsByModel = new Map(tests.map((row) => [row.model, row]));
  productionModel.textContent = latestStats.production_model || "LSTM";

  modelGrid.innerHTML = (latestStats.model_catalog || [])
    .map((model) => {
      const metrics = comparisonByModel.get(model.name);
      const description = currentLanguage === "en" ? model.description_en : model.description;
      const selectedClass = model.name === latestStats.production_model ? " is-selected" : "";
      return `
        <article class="model-card${selectedClass}">
          <div>
            <span>${modelTypeLabel(model)}</span>
            <strong>${model.name.replaceAll("_", "-")}</strong>
          </div>
          <p>${description}</p>
          <dl>
            <div><dt>${t("auc_label")}</dt><dd>${formatDecimal(metrics?.roc_auc_mean, 3)}</dd></div>
            <div><dt>${t("f1_label")}</dt><dd>${formatDecimal(metrics?.f1_mean, 3)}</dd></div>
          </dl>
        </article>
      `;
    })
    .join("");

  statsTableBody.innerHTML = comparison
    .map((row) => {
      const isSelected = row.model === latestStats.production_model;
      return `
        <tr>
          <td>${row.model.replaceAll("_", "-")}${isSelected ? " *" : ""}</td>
          <td>${formatDecimal(row.roc_auc_mean, 3)}</td>
          <td>${formatDecimal(row.f1_mean, 3)}</td>
          <td>${formatDecimal(row.fit_seconds_mean, 2)}s</td>
          <td>${isSelected ? t("selected_model") : validationSummary(testsByModel.get(row.model))}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadStatistics() {
  if (!statsTableBody) return;
  statsTableBody.innerHTML = `
    <tr>
      <td colspan="5">
        <div class="skeleton-line" style="width: 88%"></div>
        <div class="skeleton-line" style="width: 64%"></div>
      </td>
    </tr>
  `;
  refreshStatsButton.disabled = true;
  try {
    const response = await fetch(`${backendUrl}/statistics/validation`);
    if (!response.ok) throw new Error("statistics");
    latestStats = await response.json();
    renderStatistics();
  } catch {
    statsTableBody.innerHTML = `<tr><td colspan="5">${t("stats_error")}</td></tr>`;
  } finally {
    refreshStatsButton.disabled = false;
  }
}

function addChatMessage(message, type) {
  const bubble = document.createElement("div");
  bubble.className = `chat-message ${type}`;
  bubble.textContent = message;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}

async function streamChatMessage(element, text) {
  element.textContent = "";
  const chunks = String(text).split(/(\s+)/);
  for (const chunk of chunks) {
    element.textContent += chunk;
    chatMessages.scrollTop = chatMessages.scrollHeight;
    if (chunk.trim()) {
      await new Promise((resolve) => window.setTimeout(resolve, 18));
    }
  }
}

async function submitChat(event) {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  addChatMessage(message, "user");
  chatInput.value = "";
  const pending = addChatMessage(t("chat_typing"), "bot");

  try {
    const response = await fetch(`${backendUrl}/chatbot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        language: currentLanguage,
        prediction_context: buildChatPredictionContext(),
      }),
    });
    if (!response.ok) throw new Error(await readErrorMessage(response));
    const data = await response.json();
    await streamChatMessage(pending, data.answer);
  } catch (error) {
    pending.textContent = error.message || t("chat_error");
    showToast(error.message || t("chat_error"), "error");
  }
}

function openChatDrawer() {
  chatPanel.classList.add("is-open");
  chatLauncher.setAttribute("aria-expanded", "true");
  window.setTimeout(() => chatInput.focus(), 80);
}

function closeChatDrawer() {
  chatPanel.classList.remove("is-open");
  chatLauncher.setAttribute("aria-expanded", "false");
}

function setupSmoothNavigation() {
  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target) return;
      event.preventDefault();
      if (link.getAttribute("href") === "#chatbot") {
        openChatDrawer();
        return;
      }
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  const sections = ["modelos", "reportes", "chatbot"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      navLinks.forEach((link) => {
        link.classList.toggle("is-active-link", link.getAttribute("href") === `#${visible.target.id}`);
      });
    },
    { rootMargin: "-22% 0px -60% 0px", threshold: [0.16, 0.32, 0.5] },
  );
  sections.forEach((section) => observer.observe(section));
}

function setupOnboarding() {
  if (!onboarding || localStorage.getItem("afi_seen_onboarding") === "true") return;
  onboarding.hidden = false;
}

function closeOnboarding() {
  localStorage.setItem("afi_seen_onboarding", "true");
  onboarding.hidden = true;
}

function openReportFullscreen() {
  if (!reportPreview.classList.contains("has-document")) {
    setReportStatusKey("report_generating_preview");
    fetchProgramReport("pdf", { preview: true });
    return;
  }

  if (reportPreview.requestFullscreen) {
    reportPreview.requestFullscreen();
  } else if (reportFrame.src) {
    window.open(reportFrame.src, "_blank", "noreferrer");
  }
}

chatPanel.classList.add("is-drawer");
chatLauncher.setAttribute("aria-expanded", "false");

renderFields();
setPayload(baseSample);
applyLanguage();
checkHealth();
loadStatistics();
setupSmoothNavigation();
setupOnboarding();
updateWizard();
renderDriverHint();

form.addEventListener("input", () => {
  updateSnapshot();
  setReportStatusKey("report_stale");
});
form.addEventListener("submit", submitPrediction);
submitButton.addEventListener("click", submitPrediction);
resetButton.addEventListener("click", () => activateScenario("balanced"));
previewReportButton.addEventListener("click", () => fetchProgramReport("pdf", { preview: true }));
saveProfileButton.addEventListener("click", saveCurrentProfile);
profileList.addEventListener("click", handleProfileAction);
restoreLastButton.addEventListener("click", restoreLastEvaluation);
wizardPrev.addEventListener("click", () => goToWizardStep(currentWizardStep - 1));
wizardNext.addEventListener("click", () => goToWizardStep(currentWizardStep + 1, { validateCurrent: true }));
runCompareButton.addEventListener("click", runScenarioComparison);
predictionHistory.addEventListener("click", handleHistoryAction);
clearHistoryButton.addEventListener("click", clearPredictionHistory);
fullscreenReportButton.addEventListener("click", openReportFullscreen);
onboardingStart.addEventListener("click", closeOnboarding);
chatLauncher.addEventListener("click", openChatDrawer);
chatClose.addEventListener("click", closeChatDrawer);
languageToggle.addEventListener("click", () => {
  currentLanguage = currentLanguage === "es" ? "en" : "es";
  localStorage.setItem("afi_language", currentLanguage);
  applyLanguage();
});
themeToggle.addEventListener("click", () => {
  currentTheme = currentTheme === "dark" ? "light" : "dark";
  localStorage.setItem("afi_theme", currentTheme);
  applyTheme();
});
refreshStatsButton.addEventListener("click", loadStatistics);
chatForm.addEventListener("submit", submitChat);

reportButtons.forEach((button) => {
  button.addEventListener("click", () => fetchProgramReport(button.dataset.reportFormat));
});

document.querySelectorAll(".scenario-button").forEach((button) => {
  button.addEventListener("click", () => activateScenario(button.dataset.scenario));
});

wizardSteps.forEach((button) => {
  button.addEventListener("click", () => {
    const step = Number(button.dataset.step);
    goToWizardStep(step, { validateCurrent: step > currentWizardStep });
  });
});
