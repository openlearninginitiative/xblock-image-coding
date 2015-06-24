/* Javascript for Image Coding XBlock. */
function ImageCodingXBlockInitEdit(runtime, element) {

    //var xmlEditorTextarea = $('.block-xml-editor', element),
    //    xmlEditor = CodeMirror.fromTextArea(xmlEditorTextarea[0], { mode: 'xml', lineWrapping: true });

    $(element).find('.action-cancel').bind('click', function() {
        runtime.notify('cancel', {});
    });

    $(element).find('.action-save').bind('click', function() {
        var data = {
            'display_name': $('#edit_display_name').val(),
            'body': $('#edit_body').val(),
            'solution_code': $('#edit_solution_code').val(),
            'starter_code': $('#edit_starter_code').val(),
            'regex': $('#edit_regex').val(),
            'tolerance': $('#edit_tolerance').val(),
            'hints': $('#edit_hints').val()
        };
        console.log('SAVE:' + data);
        
        runtime.notify('save', {state: 'start'});
        
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            if (response.result === 'success') {
                runtime.notify('save', {state: 'end'});
                //Reload the page
                //window.location.reload(false);
            } else {
                runtime.notify('error', {msg: response.message})
            }
        });
    });
}

