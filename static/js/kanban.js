// Kanban Board Drag and Drop Functionality
document.addEventListener("DOMContentLoaded", function () {
  const columns = document.querySelectorAll(".kanban-column");

  columns.forEach((column) => {
    new Sortable(column, {
      group: "kanban",
      animation: 150,
      ghostClass: "sortable-ghost",
      dragClass: "sortable-drag",
      chosenClass: "sortable-chosen",
      onEnd: function (evt) {
        const taskId = evt.item.dataset.taskId;
        const newStatus = evt.to.dataset.status;

        // Show loading state
        evt.item.classList.add("loading");

        // Update task status via API
        fetch("/tasks/api/task/status/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({
            task_id: taskId,
            status: newStatus,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            evt.item.classList.remove("loading");
            if (!data.success) {
              // Revert on failure
              alert("Failed to update task status");
              evt.item.remove();
              evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
            } else {
              // Show success feedback
              showToast("Task status updated successfully", "success");
            }
          })
          .catch((error) => {
            evt.item.classList.remove("loading");
            console.error("Error:", error);
            alert("Failed to update task. Please refresh the page.");
            // Revert on error
            evt.item.remove();
            evt.from.insertBefore(evt.item, evt.from.children[evt.oldIndex]);
          });
      },
    });
  });
});

// Helper function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Toast notification function
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 ${
    type === "success"
      ? "bg-green-500"
      : type === "error"
      ? "bg-red-500"
      : "bg-blue-500"
  }`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
