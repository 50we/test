document.getElementById('FeedbackForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const authToken = localStorage.getItem('Authorization');
    let formData = new FormData();
    let text = document.getElementById('feedback');
    var input = document.querySelector('input[type="file"]');
    let url = document.getElementById('link');
    formData.append("feedback", text.value);
    formData.append('file', input.files[0]);
    formData.append('url', text.value)

    fetch('http://localhost:8000/clients', {
        method: 'POST',
        headers: {
            'X-Authorization': authToken
        },
        body: formData
    })
        .then(response => response.text()) // Get the response text
        .then(html => {
            document.documentElement.innerHTML = html; // Replace the entire HTML of the page
        })
        .catch(error => {
            console.error('Error fetching the HTML:', error);
        });
});
