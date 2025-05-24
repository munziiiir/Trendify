// checkout button
$(document).on('click', '#checkout-button', function () {
    const prices = document.querySelectorAll('.price');
    const quantities = document.querySelectorAll('input');
    const checkoutPrices = document.querySelectorAll('.checkout-price');

    if (prices.length != quantities.length || prices.length != checkoutPrices.length) {
        console.error(`Mismatched number of elements: ${prices.length} and ${quantities.length} and ${checkoutPrices.length}`);
        return;
    }

    prices.forEach((priceElement) => {
        const index = priceElement.getAttribute('data-index');
        const quantityElement = Array.from(quantities).find(input => input.getAttribute('data-index') == index);
        const checkoutPriceElement = Array.from(checkoutPrices).find(checkout => checkout.getAttribute('data-index') == index);

        if (quantityElement && checkoutPriceElement) {
            const price = parseFloat(priceElement.textContent.replace('$', '')) || 0;
            const quantity = parseFloat(quantityElement.value) || 0;
            const total = price * quantity
            checkoutPriceElement.textContent = total.toFixed(2);
        } else {
            console.error(`Data-index missing or mismatched`)
        }
    })
})

// update button
$(document).on('click', '#update-cart', function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: cartUpdateUrl,
        data: {
            pid: $(this).data('index'),
            qty: $('#qty' + $(this).data('index')).val(),
            csrfmiddlewaretoken: csrfToken,
            action: 'post'
        },
        success: function (json) { location.reload() },
        error: function (xhr, status, error) { }
    });
});


// delete button
$(document).on('click', '#delete-cart', function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: cartDeleteUrl,
        data: {
            pid: $(this).data('index'),
            csrfmiddlewaretoken: csrfToken,
            action: 'post'
        },
        success: function (json) { location.reload() },
        error: function (xhr, status, error) { }
    });
});