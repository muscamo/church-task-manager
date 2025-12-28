// Gantt Chart JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // Simple Gantt chart enhancements

  // Add date range indicator
  const addDateRangeIndicator = () => {
    const today = new Date();
    const indicators = document.querySelectorAll("[data-date-indicator]");

    indicators.forEach((indicator) => {
      const taskDate = new Date(indicator.dataset.date);
      if (taskDate < today) {
        indicator.classList.add("text-red-600", "font-semibold");
      }
    });
  };

  addDateRangeIndicator();

  // Add tooltips for task details
  const taskRows = document.querySelectorAll("tbody tr");
  taskRows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.backgroundColor = "#f9fafb";
    });

    row.addEventListener("mouseleave", function () {
      this.style.backgroundColor = "";
    });
  });
});
