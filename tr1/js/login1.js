document.getElementById('Login').addEventListener('submit', function (event) {
    event.preventDefault();

    let username = document.getElementById('username').value;
    let passwd = document.getElementById('password').value;
    let redirect_link = 'http://localhost:8000/users/' + username;

    let data = {
        username: username,
        plain_password: passwd
    };

    fetch('http://localhost:8000/auth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                document.getElementById('Login').addEventListener('submit', function (event) {
                    event.preventDefault();

                    let username = document.getElementById('username').value;
                    let passwd = document.getElementById('password').value;
                    let redirect_link = 'http://localhost:8000/users/' + username;

                    let data = {
                        username: username,
                        plain_password: passwd
                    };

                    fetch('http://localhost:8000/auth/token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                        .then(response => {
                            if (response.ok) {
                                return response.json();
                            } else {
                                // Handle errors or non-redirect responses
                                console.error('Request failed');
                            }
                        })
                        .then(data => {
                            // assuming the token is in the 'token' property of the response data
                            const token = data.access_token;
                            const type = data.token_type;
                            let authToken = `${type} ${token}`;
                            localStorage.setItem('X-Authorization', authToken); // store the token in local storage

                            // If the response is successful, redirect to another URL
                            window.location.href = redirect_link;
                        })
                        .catch((error) => {
                            console.error('Error:', error);
                        });
                });
            } else {
                // Handle errors or non-redirect responses
                console.error('Request failed');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});