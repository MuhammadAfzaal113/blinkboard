document.addEventListener("DOMContentLoaded", function () {
    var loginForm = document.getElementById("login-form");

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();

            var username = document.getElementById("login__username").value;
            var password = document.getElementById("login__password").value;

            var data = {
                username: username,
                password: password,
            };

            // Fetch CSRF token from cookies
            var csrftoken = getCookie('csrftoken');
            console.log(csrftoken)
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "http://192.168.0.103:8000/login/", true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

            // Include CSRF token in the headers
            xhr.setRequestHeader("X-CSRFToken", csrftoken);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        document.querySelector(".form__alert").textContent = 'Logged In Successfully!';
                        window.location.href = '/your-successful-login-redirect/';
                    } else {
                        document.querySelector(".form__alert").textContent = 'Login Failed!';
                    }
                } else {
                    console.error('Error:', xhr.status, xhr.statusText);
                    document.querySelector(".form__alert").textContent = 'Login Failed!';
                }
            };

            xhr.onerror = function () {
                console.error('Network error occurred');
                document.querySelector(".form__alert").textContent = 'Login Failed!';
            };

            xhr.send(JSON.stringify(data));
        });
    } else {
        console.error('Login form not found');
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
