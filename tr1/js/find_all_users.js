// Make a request to the server

function maskString(str, start, end) {
    if (!str || start < 0 || end > str.length) {
      return str;
    }
    const maskLength = end - start;
    const maskedPart = '*'.repeat(maskLength);
    return str.slice(0, start) + maskedPart + str.slice(end);
  }

document.getElementById('myForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let name = document.getElementById('name').value;

    let data = {
        name: name,
    };

    fetch('/clients/find_one', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
    // Check if the request was successful
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
    // Extract the data in JSON format
        return response.json();
    })
  .then(data => {
    // Assuming 'data' is an array and we have a container in our HTML with the ID 'data-container'
    const container = document.getElementById('username');
    // Iterate through the array of data
    data.forEach(item => {
      document.getElementById('userroles').textContent = maskString(item[3], 1,4);
      document.getElementById('username').textContent = item[1];
    });
  })
  .catch(error => {
    // Handle any errors that occurred during the fetch
    console.error('There was a problem with the fetch operation:', error);
  });
})