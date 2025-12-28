// Dashboard JavaScript for additional interactivity
document.addEventListener("DOMContentLoaded", function () {
  // Add any dashboard-specific JavaScript here

  // Example: Auto-refresh dashboard every 5 minutes
  const AUTO_REFRESH_INTERVAL = 300000; // 5 minutes in milliseconds

  // Uncomment to enable auto-refresh
  // setTimeout(() => {
  //     location.reload();
  // }, AUTO_REFRESH_INTERVAL);

  // Add hover effects to stat cards
  const statCards = document.querySelectorAll(".bg-white.rounded-lg.shadow");
  statCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px)";
      this.style.boxShadow = "0 10px 15px -3px rgba(0, 0, 0, 0.1)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
      this.style.boxShadow = "0 1px 3px 0 rgba(0, 0, 0, 0.1)";
    });
  });
});
