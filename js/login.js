// Adds event listners for warning messages tied to username/password inputs.
clearWarningOnInput('inputUsername', 'warning-msg-user-login');
clearWarningOnInput('inputPassword', 'warning-msg-pwd-login');

// Sends login request to server.
(function doLogin() {
  var form = document.getElementById('account-form');
  addEvent(form, 'submit', function(e) {
    e.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4 && xhr.status == 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.success) {
          window.location.assign('/');
        } else if (response.baduser) {
          document.getElementById('bad-username').innerText = response.user;
          var cl = document.getElementById('warning-msg-user-login').classList;
          cl.remove('hidden-warning');
          var inputBox = document.getElementById('inputUsername');
          inputBox.value = '';
          inputBox.focus();
        } else {
          // Bad password
          document.getElementById('bad-password').innerText = response.user;
          var cl = document.getElementById('warning-msg-pwd-login').classList;
          cl.remove('hidden-warning');
          var inputBox = document.getElementById('inputPassword');
          inputBox.value = '';
          inputBox.focus();
        }
      }
    };
    var user = form.elements.user.value;
    var pwd = form.elements.password.value;
    var msg = JSON.stringify({'user': user, 'password': pwd});
    xhr.open('POST', '/do-login', true);
    xhr.send(msg);
  });
})();
