function updateMessage(msg) {
    var tpl = '<div class="alert alert-info">' +
              '<button class="close" data-dismiss="alert" type="button">x</button>' +
        msg + '</div>';
    jQuery('#pageContent > .alert').remove();
    jQuery('#pageContent').prepend($(tpl));
}