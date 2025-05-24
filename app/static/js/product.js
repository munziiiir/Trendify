$(document).on('click', '#addcart', function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: cartAddUrl,
        data: {
            pid: $(this).val(),
            qty: $(qty).val(),
            csrfmiddlewaretoken: csrfToken,
            action: 'post'
        },
        success: function (json) {
            console.log(json);
            try {
                document.getElementById('cartQuantity').textContent = json.cartQty;
            } finally {
                location.reload()
            }
        },
        error: function (xhr, status, error) { }
    });
});