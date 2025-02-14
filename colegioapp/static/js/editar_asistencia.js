document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('asistenciaForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const url = form.dataset.url;
            
            // Resetear mensajes de error previos
            document.getElementById('estadoError').textContent = '';
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    alert(data.message);
                    // Redirigir a la lista de asistencias
                    window.location.href = form.querySelector('a').href;
                } else {
                    // Mostrar errores si existen
                    if (data.errors && data.errors.estado) {
                        document.getElementById('estadoError').textContent = data.errors.estado[0];
                        document.getElementById('id_estado').classList.add('is-invalid');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ha ocurrido un error al actualizar la asistencia');
            });
        });
    }
});