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


// V6 background grid and quote rotator
const bgImages = ["/static/assets/elevator_01.webp", "/static/assets/elevator_02.webp", "/static/assets/elevator_03.webp", "/static/assets/elevator_04.jpeg", "/static/assets/elevator_05.webp", "/static/assets/elevator_06.webp", "/static/assets/elevator_07.webp", "/static/assets/elevator_08.webp", "/static/assets/elevator_09.webp"];
const bgGrid = document.querySelector(".anime-bg-grid");
if(bgGrid && bgImages.length){
  bgImages.forEach(src => {
    const cell = document.createElement("div");
    cell.className = "bg-cell";
    cell.style.backgroundImage = `url('${src}')`;
    bgGrid.appendChild(cell);
  });
}

const quoteRotator = document.getElementById("quoteRotator");
const quoteText = document.getElementById("quoteText");
if(quoteRotator && quoteText){
  let quotes = [];
  try {
    quotes = JSON.parse(quoteRotator.dataset.quotes || "[]");
  } catch(e) {}
  let idx = 0;
  if(quotes.length > 1){
    setInterval(() => {
      idx = (idx + 1) % quotes.length;
      quoteText.style.opacity = "0";
      setTimeout(() => {
        quoteText.textContent = quotes[idx];
        quoteText.style.opacity = "1";
      }, 250);
    }, 30000);
  }
}


// V7 ensure background grid fills all 9 cells visibly
(function(){
  const grid = document.querySelector(".anime-bg-grid");
  if(!grid) return;

  const existing = Array.from(grid.querySelectorAll(".bg-cell"));
  if(existing.length >= 9) return;

  const fallbackImages = [
    "/static/assets/elevator_01.webp",
    "/static/assets/elevator_02.webp",
    "/static/assets/elevator_03.webp",
    "/static/assets/elevator_04.jpeg",
    "/static/assets/elevator_05.webp",
    "/static/assets/elevator_06.webp",
    "/static/assets/elevator_07.webp",
    "/static/assets/elevator_08.webp",
    "/static/assets/elevator_09.webp"
  ];

  grid.innerHTML = "";
  fallbackImages.forEach(src => {
    const cell = document.createElement("div");
    cell.className = "bg-cell";
    cell.style.backgroundImage = `url('${src}')`;
    grid.appendChild(cell);
  });
})();

// V9 meal/body intelligence
const mealModal = document.getElementById("mealModal"); const bodyModal = document.getElementById("bodyModal");
document.querySelectorAll("[data-open-meal]").forEach(btn=>btn.addEventListener("click",()=>mealModal.showModal()));
document.querySelectorAll("[data-open-body]").forEach(btn=>btn.addEventListener("click",()=>bodyModal.showModal()));
document.querySelectorAll("[data-open-category]").forEach(btn=>{btn.addEventListener("click",(e)=>{if(btn.dataset.title==="Meal Tracking"){e.stopImmediatePropagation();e.preventDefault();mealModal.showModal();} if(btn.dataset.title==="Body Metrics"){e.stopImmediatePropagation();e.preventDefault();bodyModal.showModal();}}, true);});
window.addEventListener("DOMContentLoaded",()=>{const canvas=document.getElementById("nutritionChart"); if(!canvas||!window.Chart)return; const payload=JSON.parse(canvas.dataset.chart); new Chart(canvas,{type:"bar",data:{labels:payload.labels,datasets:[{label:"Sugar g",data:payload.sugar||[],backgroundColor:"#ff3b30"},{label:"Protein g",data:payload.protein||[],backgroundColor:"#6cff2d"},{label:"Sodium mg / 100",data:(payload.sodium||[]).map(v=>Math.round(v/100)),backgroundColor:"#ffd21f"}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:"#d8dce6"}}},scales:{x:{ticks:{color:"#a7adba"},grid:{color:"rgba(255,255,255,.05)"}},y:{ticks:{color:"#a7adba"},grid:{color:"rgba(255,255,255,.05)"}}}}});});


// V10 force category modal color scheme every time it opens
document.querySelectorAll("[data-open-category]").forEach(btn => {
  btn.addEventListener("click", () => {
    const modal = document.getElementById("categoryModal");
    if(!modal) return;
    const color = btn.dataset.color || "red";
    modal.className = "modal category-modal modal-" + color;
    document.documentElement.style.setProperty("--active-category-color", color);
  }, true);
});
