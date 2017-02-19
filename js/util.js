/* Helper function to add an event listener.
 * @param {Element} el - The element we want to add an event listener to.
 * @param {Event} event - The event we want to listen to.
 * @param {function} callback - The callback function to call when the event is
 * transmitted.
 */
function addEvent(el, event, callback) {
  if ('addEventListener' in el) {
    el.addEventListener(event, callback, false);
  } else {
    el['e' + event + callback] = callback;
    el[event + callback] = function() {
      el['e' + event + callback](window.event);
    };
    el.attachEvent('on' + event, el[event + callback]);
  }
}

/* Removes warning message from login or register page as soon as user begins
 * typing a new username or password.
 * @param {string} inputId - The ID of the input element.
 * @param {string} warningId - The ID of the warning element.
 */
function clearWarningOnInput(inputId, warningId) {
  var el= document.getElementById(inputId);
  addEvent(el, 'input', function() {
    var cl = document.getElementById(warningId).classList;
    if (!cl.contains('hidden-warning')) {
      cl.add('hidden-warning');
    }
  });
}
