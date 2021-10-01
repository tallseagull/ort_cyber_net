// Listen to the 'submit' button:
const form = document.getElementById("reset-form");

function RemoveLastDirectoryPartOf(the_url)
{
    var the_arr = the_url.split('/');
    the_arr.pop();
    return( the_arr.join('/') );
}
// Get the base path:
var base_path = RemoveLastDirectoryPartOf(window.location);

form.addEventListener("submit", function(event) {
    // handle the form data - get the passwords, compare them, and if they match reset the password:
    var new_pass1 = document.getElementById('pass1').value;
    var new_pass2 = document.getElementById('pass2').value;

    console.log(new_pass1)
    console.log(new_pass2)

    // prevent the form submission
    event.preventDefault();

    if (new_pass1 == new_pass2) {
        // POST the password to reset it:
        $.post(base_path + '/submit_new_passwd',
              {'passwd': new_pass1},
              function (response){
                  // Get us to the 'thank you' page:
                  console.log(response)
                  if (response === 'error') {
                      alert("Sorry, password reset failed")
                  }
                  else {
                      // Redirect to the page we received:
                      location.href = response
                  }
              })
    }
    else {
        alert("Passwords do not match!")
    }
});