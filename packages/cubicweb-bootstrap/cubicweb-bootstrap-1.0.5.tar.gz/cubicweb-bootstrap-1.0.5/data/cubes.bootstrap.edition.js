/**
 * monkeypatching of cubicweb.edition.js
 */

/**
 * copied from cw 3.19.0, clears the new classes added by
 * _displayValidationerrors() below
 */
function _clearPreviousErrors(formid) {
    // on some case (eg max request size exceeded, we don't know the formid
    if (formid) {
        jQuery('#' + formid + 'ErrorMessage').remove();
        jQuery('#' + formid + ' span.errorMsg').remove();
        jQuery('#' + formid + ' .error').removeClass('error');
        jQuery('#' + formid + ' .has-error').removeClass('has-error');
    } else {
        jQuery('span.errorMsg').remove();
        jQuery('.error').removeClass('error');
        jQuery('.has-error').removeClass('has-error');
    }
}

/**
 * copied from cw 3.19.0, adds :
 *  - the 'help-block' class on the error message span
 *  - the 'has-error' class on the parent 'form-group' div
 *  - the 'alert-danger' class on the global error message div
 */
function _displayValidationerrors(formid, eid, errors) {
    var globalerrors = [];
    var firsterrfield = null;
    for (fieldname in errors) {
        var errmsg = errors[fieldname];
        if (!fieldname) {
            globalerrors.push(errmsg);
        } else {
            var fieldid = fieldname + ':' + eid;
            var suffixes = ['', '-subject', '-object'];
            var found = false;
            // XXX remove suffixes at some point
            for (var i = 0, length = suffixes.length; i < length; i++) {
                var field = cw.jqNode(fieldname + suffixes[i] + ':' + eid);
                if (field && jQuery(field).attr('type') != 'hidden') {
                    if (!firsterrfield) {
                        firsterrfield = 'err-' + fieldid;
                    }
                    jQuery(field).addClass('error');
                    var span = SPAN({
                        'id': 'err-' + fieldid,
                        'class': "errorMsg help-block"
                    },
                    errmsg);
                    field.before(span);
                    field.closest('.form-group').addClass('has-error');
                    found = true;
                    break;
                }
            }
            if (!found) {
                firsterrfield = formid;
                globalerrors.push(_(fieldname) + ' : ' + errmsg);
            }
        }
    }
    if (globalerrors.length) {
       if (globalerrors.length == 1) {
           var innernode = SPAN(null, globalerrors[0]);
       } else {
           var linodes =[];
           for(var i=0; i<globalerrors.length; i++){
             linodes.push(LI(null, globalerrors[i]));
           }
           var innernode = UL(null, linodes);
       }
        // insert DIV and innernode before the form
        var div = DIV({
            'class': "errorMessage alert alert-danger",
            'id': formid + 'ErrorMessage'
        });
        div.appendChild(innernode);
        jQuery('#' + formid).before(div);
    }
    return firsterrfield || formid;
}
