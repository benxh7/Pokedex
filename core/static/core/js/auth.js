document.addEventListener('DOMContentLoaded', function() {
    // Checkbox que activa/desactiva mostrar contraseña
    const showPasswordCheckbox = document.getElementById("showPassword");

    // Los campos generados por Django UserCreationForm suelen tener IDs "id_password1" y "id_password2"
    const password1Field = document.getElementById("id_password1");
    const password2Field = document.getElementById("id_password2");
    const passwordField = document.getElementById("password");

    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener('change', function() {
            // Si está marcado, mostraremos las contraseñas en texto plano
            const newType = this.checked ? 'text' : 'password';
            if (password1Field) password1Field.type = newType;
            if (password2Field) password2Field.type = newType;
            if (passwordField) passwordField.type = newType;
        });
    }
});