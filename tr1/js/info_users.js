document.getElementById('myForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let name = document.getElementById('name').value;

    let data = {
        name: name,
    };

    fetch('http://localhost:8000/clients/find', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text()) // Get the response text
    .then(html => {
        document.documentElement.innerHTML = html; // Replace the entire HTML of the page
    })
    .catch(error => {
        console.error('Error fetching the HTML:', error);
    });
});