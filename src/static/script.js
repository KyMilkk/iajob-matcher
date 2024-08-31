// Función para convertir CSV a JSON
function parseCSV(data) {
    const lines = data.trim().split('\n');
    const headers = lines.shift().split(','); // Extraer encabezados de la primera línea

    return lines.map(line => {
        const values = line.split(',');
        return headers.reduce((acc, header, index) => {
            acc[header] = values[index] ? values[index].trim() : ''; // Manejar valores faltantes
            return acc;
        }, {});
    });
}

// Función para renderizar los trabajos en el HTML
function renderJobs(jobs) {
    const jobListingContainer = document.querySelector('.job-listing');
    jobListingContainer.innerHTML = '';

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.classList.add('job-card');
        jobCard.innerHTML = `
            <h4>${job.job_title}</h4>
            <p>Empresa: ${job.company_name}</p>
            <p>Ubicación: ${job.location}</p>
            <p>Fecha de Inicio: ${job.start_date}</p>
            <p>CTC: ${job.ctc}</p>
            <p>Experiencia: ${job.experience}</p>
            <button>Ver Detalles</button>
        `;
        jobListingContainer.appendChild(jobCard);
    });
}

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    fetch('data/processed/processed_jobs.csv')  // Ajusta la ruta según la ubicación del archivo CSV
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(csvText => {
            const jobs = parseCSV(csvText);
            renderJobs(jobs); // Renderizar todos los trabajos
        })
        .catch(error => console.error('Error al cargar el archivo CSV:', error));
});

// Código para manejar el formulario (si existe en tu proyecto)
document.getElementById('user-form')?.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevenir el envío estándar del formulario

    const formData = new FormData(this); // Crear un objeto FormData con los datos del formulario

    // Realizar la solicitud POST al servidor
    fetch('/generate-cv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Convertir la respuesta en JSON
    .then(data => {
        // Manejar la respuesta, por ejemplo, mostrar el CV generado
        document.getElementById('cv-output').innerHTML = data.cvHtml; // Mostrar el CV en el div con id "cv-output"
    })
    .catch(error => console.error('Error:', error)); // Manejar errores
});
