document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle book availability updates
    document.querySelectorAll('.book-quantity').forEach(function(element) {
        const available = parseInt(element.dataset.available);
        const total = parseInt(element.dataset.total);
        
        if (available === 0) {
            element.classList.add('book-status-unavailable');
        } else if (available === total) {
            element.classList.add('book-status-available');
        }
    });

    // Automatically highlight overdue items
    document.querySelectorAll('.borrow-record').forEach(function(element) {
        const dueDate = new Date(element.dataset.dueDate);
        const status = element.dataset.status;
        
        if (status === 'borrowed' && new Date() > dueDate) {
            element.classList.add('overdue');
        }
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});