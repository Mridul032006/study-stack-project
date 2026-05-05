// ✅ Check if JS is working
console.log("JS Connected Successfully");


// ===============================
// BUTTON CLICK EFFECT
// ===============================
document.querySelectorAll(".btn").forEach(button => {
    button.addEventListener("click", () => {
        button.style.transform = "scale(0.95)";
        setTimeout(() => {
            button.style.transform = "scale(1)";
        }, 150);
    });
});


// ===============================
// FORM ALERT (UPLOAD PAGE)
// ===============================
const form = document.querySelector("form");

if (form) {
    form.addEventListener("submit", () => {
        alert("✅ Your note is being uploaded!");
    });
}


// ===============================
// SMOOTH SCROLL
// ===============================
document.querySelectorAll("a[href^='#']").forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({
                behavior: "smooth"
            });
        }
    });
});


// ===============================
// HOVER EFFECT FOR CARDS
// ===============================
document.querySelectorAll(".card, .note-card").forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.boxShadow = "0 10px 25px rgba(0,0,0,0.2)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.boxShadow = "0 5px 15px rgba(0,0,0,0.1)";
    });
});


// ===============================
// TOGGLE CHARTS
// ===============================
function toggleCharts() {
    const section = document.getElementById("chartsSection");

    if (section) {
        section.style.display =
            (section.style.display === "none") ? "grid" : "none";
    }
}


// ===============================
// 📊 DYNAMIC CHART (FROM FLASK)
// ===============================

if (typeof chartLabels !== "undefined" && typeof chartData !== "undefined") {

    const ctx1 = document.getElementById("subjectChart");

    if (ctx1) {
        new Chart(ctx1, {
            type: "doughnut",
            data: {
                labels: chartLabels,
                datasets: [{
                    data: chartData
                }]
            }
        });
    }
}