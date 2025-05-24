document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".auto-dismiss-alert");
    alerts.forEach(alert => {
        let isHovered = false;
        alert.addEventListener("mouseenter", () => { isHovered = true });
        alert.addEventListener("mouseleave", () => { isHovered = false });

        setTimeout(function autoDismiss() {
            if (!isHovered) {
                const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
                alertInstance.close();
            } else { setTimeout(autoDismiss, 3000) }
        }, 5000);
    });
});