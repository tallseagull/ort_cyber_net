
function RemoveLastDirectoryPartOf(the_url)
{
    var the_arr = the_url.split('/');
    the_arr.pop();
    return( the_arr.join('/') );
}

var base_path = RemoveLastDirectoryPartOf(window.location.pathname);

function tableFromJson(tableData) {

    // Extract value from table header.
    var col = [];
    for (var i = 0; i < tableData.length; i++) {
        for (var key in tableData[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    // Create a table.
    var table = document.createElement("table");
    table.setAttribute("class", "fl-table");

    // Create table header row using the extracted headers above.
    var tr = table.insertRow(-1);                   // table row.

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // table header.
        th.innerHTML = col[i];
        tr.appendChild(th);
    }

    // add json data to the table as rows.
    for (var i = 0; i < tableData.length; i++) {

        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
            tabCell.innerHTML = tableData[i][col[j]];
        }
    }

    // Now, add the newly created table with json data, to a container.
    var divShowData = document.getElementById('showData');
    divShowData.innerHTML = "";
    divShowData.appendChild(table);
}

// Get the user profiles JSON from the server:
$.post(base_path + '/view', {'src': 'server/main_user_profile.json'},
  function (response){
      // Populate the table with the response JSON:
      console.log(response)
      tableFromJson(JSON.parse(response));
  });

function showNav(item) {
    // Show an item by name - either 'users', 'restart' or 'upload'
    if (item==='users') {
        document. getElementById("users"). style. display = "block";
        document. getElementById("restart"). style. display = "none";
        document. getElementById("upload"). style. display = "none";
    }
    if (item==='restart') {
        document. getElementById("users"). style. display = "none";
        document. getElementById("restart"). style. display = "block";
        document. getElementById("upload"). style. display = "none";
    }
    if (item==='upload') {
        document. getElementById("users"). style. display = "none";
        document. getElementById("restart"). style. display = "none";
        document. getElementById("upload"). style. display = "block";
    }
}

showNav("users");

document.getElementById("users-tab").addEventListener("click", function() {
    showNav("users");
});
document.getElementById("restart-tab").addEventListener("click", function() {
    showNav("restart");
});
document.getElementById("upload-tab").addEventListener("click", function() {
    showNav("upload");
});

document.getElementById("restart-button").addEventListener("click", function () {
    $.post(base_path + "/restart")
});



// Listen to the search button to update the selected items:
$('#upload-form').submit(function(e){
    $.ajax({
      url: $('#upload-form').attr('action'),
      type: 'POST',
      data : new FormData( this ),
        processData: false,
      contentType: false,
      success: function(response){
        alert(response);
      }
    });
    e.preventDefault();
    return false;
});