$(document).ready(function() {
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file-uploader'),
        // path to server-side upload script
        action: '/upload',

        onComplete: function(id, filename, responseJSON){
            var li = $('.qq-upload-success:last')[0];
            var a = document.createElement('a');
            var link = window.location.protocol
                     + '//'
                     + window.location.host
                     + '/download/'
                     + responseJSON.filename
                     + '#'
                     + responseJSON.key;
            a.setAttribute('href', link);
            a.appendChild(document.createTextNode(link));
            li.appendChild(a);
        },

    }); 
})
