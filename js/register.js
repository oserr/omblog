// Adds event listners for warning messages tied to username/password inputs.
clearWarningOnInput('inputUsername', 'warning-msg-register');

// Sends registration request to server.
(function doRegister() {
  var form = document.getElementById('account-form');
  addEvent(form, 'submit', function(e) {
    e.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4 && xhr.status == 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.success) {
          window.location.assign('/');
        } else {
          document.getElementById('username-taken').innerText = response.user;
          var cl = document.getElementById('warning-msg-register').classList;
          cl.remove('hidden-warning');
          var nameBox = document.getElementById('inputUsername');
          nameBox.value = '';
          nameBox.focus();
        }
      }
    };
    var user = form.elements.user.value;
    var pwd = form.elements.password.value;
    var msg = JSON.stringify({'user': user, 'password': pwd});
    xhr.open('POST', '/do-register', true);
    xhr.send(msg);
  });
})();
