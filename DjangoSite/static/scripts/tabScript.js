document.addEventListener("DOMContentLoaded", function() {
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const tabId = button.getAttribute("data-tab");
            
            tabButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            tabContents.forEach(content => {
                content.classList.remove("active");
                let value = content.getElementsByTagName("details");
                if (content.id === tabId) {
                    content.classList.add("active");
                    value.open = true;
                }
                else {
                    value.open = false;
                }
            });
        });
    });
});
