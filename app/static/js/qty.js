// &plus button
function m(btn) {
    const input = btn.nextElementSibling;
    if (input.value > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// &minus button
function p(btn) {
    const input = btn.previousElementSibling;
    if (input.value < 50) {
        input.value = parseInt(input.value) + 1;
    }
}