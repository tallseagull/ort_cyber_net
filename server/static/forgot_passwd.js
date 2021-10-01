// Listen to the 'submit' button:
const form = document.getElementById("forgot_form");

form.addEventListener("submit", function(event) {
  // handle the form data - prevent the form submission
    event.preventDefault();

    // POST the details to get the password reset link:
    $.post('/recovery_qs',
          {
              'name': document.getElementById('name').value,
              'first_car': document.getElementById('first_car').value,
              'birth_place': document.getElementById('birth_place').value
          },
          function (response){
              // Get us to the 'thank you' page:
              console.log(response)
              if (response === 'error') {
                  alert("Sorry, password reset data is incorrect")
              }
              else {
                  // Redirect to the page we received:
                  location.href = response
              }
          })
});