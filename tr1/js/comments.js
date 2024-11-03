document.getElementById('Comment').addEventListener('submit', function(event) {
    event.preventDefault();

    let comment = document.getElementById('comment').value;

    const currentUrl = window.location.href;

    let data = {
        comment: comment,
    };

    fetch(currentUrl, {
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