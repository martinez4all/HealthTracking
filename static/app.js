const logModal = document.getElementById("logModal");
const goalsModal = document.getElementById("goalsModal");
const dynamicField = document.getElementById("dynamicField");
const logTitle = document.getElementById("logTitle");

const fieldLabels = {
  food: ["calories", "Calories", "number", "Example: 650"],
  water_oz: ["water_oz", "Water oz", "number", "Example: 32"],
  workouts: ["workouts", "Workout Count", "number", "Example: 1"],
  power_drills: ["power_drills", "Power Drills", "number", "Example: 1"],
  saq_minutes: ["saq_minutes", "SAQ Minutes", "number", "Example: 15"],
  sleep_hours: ["sleep_hours", "Sleep Hours", "number", "Example: 6.5"],
  body_weight: ["body_weight", "Body Weight", "number", "Example: 214.5"],
  recovery_minutes: ["recovery_minutes", "Recovery Minutes", "number", "Example: 10"],
  supplements: ["supplements", "Supplements / Medication Done", "number", "Example: 1"],
  notes: ["notes", "Reflection", "textarea", "Write your truth for today."]
};

function openLog(field, title){
  const config = fieldLabels[field] || fieldLabels.notes;
  logTitle.textContent = title;
  if(config[2] === "textarea"){
    dynamicField.innerHTML = `<label>${config[1]}<textarea name="${config[0]}" placeholder="${config[3]}"></textarea></label>`;
  } else {
    dynamicField.innerHTML = `<label>${config[1]}<input name="${config[0]}" type="${config[2]}" step="0.1" placeholder="${config[3]}" autofocus></label>`;
    if(field === "food"){
      dynamicField.innerHTML += `<label>Protein g<input name="protein_g" type="number" step="1" placeholder="Example: 45"></label>`;
    }
  }
  logModal.showModal();
}

document.querySelectorAll("[data-open-log]").forEach(btn=>{
  btn.addEventListener("click",()=>openLog(btn.dataset.field, btn.dataset.title));
});
document.querySelectorAll("[data-open-goals]").forEach(btn=>btn.addEventListener("click",()=>goalsModal.showModal()));
document.querySelectorAll("[data-close]").forEach(btn=>btn.addEventListener("click",()=>btn.closest("dialog").close()));

window.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("weeklyChart");
  if(!canvas || !window.Chart) return;

  const payload = JSON.parse(canvas.dataset.chart);
  new Chart(canvas, {
    type: "line",
    data: {
      labels: payload.labels,
      datasets: [
        { label: "Workouts", data: payload.workouts, borderColor: "#ff3b30", backgroundColor: "#ff3b30", tension: .35, yAxisID: "y" },
        { label: "Calories", data: payload.calories, borderColor: "#6cff2d", backgroundColor: "#6cff2d", tension: .35, yAxisID: "y1" },
        { label: "Sleep", data: payload.sleep, borderColor: "#b84cff", backgroundColor: "#b84cff", tension: .35, yAxisID: "y" }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#d8dce6", boxWidth: 8, usePointStyle: true } } },
      scales: {
        x: { ticks: { color: "#a7adba" }, grid: { color: "rgba(255,255,255,.06)" } },
        y: { ticks: { color: "#a7adba" }, grid: { color: "rgba(255,255,255,.06)" } },
        y1: { position: "right", ticks: { color: "#a7adba" }, grid: { drawOnChartArea: false } }
      }
    }
  });
});


// V5 category image modal
const categoryModal = document.getElementById("categoryModal");
const categoryModalBg = document.getElementById("categoryModalBg");
const categoryModalTitle = document.getElementById("categoryModalTitle");
const categoryModalSubtitle = document.getElementById("categoryModalSubtitle");
const categoryLogButton = document.getElementById("categoryLogButton");
let pendingCategory = null;

document.querySelectorAll("[data-open-category]").forEach(btn => {
  btn.addEventListener("click", () => {
    pendingCategory = {
      field: btn.dataset.field,
      title: btn.dataset.title,
      subtitle: btn.dataset.subtitle
    };
    categoryModalBg.style.backgroundImage = `url('${btn.dataset.image}')`;
    categoryModalTitle.textContent = btn.dataset.title;
    categoryModalSubtitle.textContent = btn.dataset.subtitle;
    categoryModal.showModal();
  });
});

if(categoryLogButton){
  categoryLogButton.addEventListener("click", () => {
    if(!pendingCategory) return;
    categoryModal.close();
    openLog(pendingCategory.field, pendingCategory.title);
  });
}
