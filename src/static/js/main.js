console.log('Application loaded');

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.main-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted');
        });
    }
});
