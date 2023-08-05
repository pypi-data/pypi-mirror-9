function edit_title(doc_id, elt) {
    //noinspection JSLint
    $('#loading_title').removeClass('hidden');
    $.ajax({url: '/updoc/edit/' + doc_id + '/', type: 'POST', data: {'name': elt.textContent},
        'success': function () {$('#loading_title').addClass('hidden'); }});
}

function edit_keywords(doc_id, elt) {
    //noinspection JSLint
    $('#loading_keywords').removeClass('hidden');
    $.ajax({url: '/updoc/edit/' + doc_id + '/', type: 'POST', data: {'keywords': elt.textContent},
        'success': function () {$('#loading_keywords').addClass('hidden'); }});
}
