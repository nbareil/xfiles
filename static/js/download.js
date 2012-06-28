$(document).ready(function() {
    var key = window.location.hash.slice(1);
    var keyInput = $('#keyInput')[0];
    keyInput.setAttribute('type', 'hidden');
    $('label')[0].setAttribute('style', 'display: none')
    keyInput.value = key;
    $('form').submit();
});
