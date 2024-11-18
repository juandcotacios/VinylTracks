document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', () => {
        alert('Producto añadido al carrito');
    });
});

function loginFunc() {
    fetch('api/login/')
    .then(Response => Response.json)
    .then(data => {
        window.location.href = '/api/login/';
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function RegisterFunc() {
    fetch('api/register/')
    .then(Response => Response.json)
    .then(data => {
        window.location.href = '/api/register/';
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
