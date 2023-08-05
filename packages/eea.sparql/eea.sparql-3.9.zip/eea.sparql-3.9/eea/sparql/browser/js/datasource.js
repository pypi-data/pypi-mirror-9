$(document).ready(function() {

    function setDataGridWidgetTRLabels() {
    $('#datagridwidget-tbody-arg_spec')
        .find('.eea-sparql-datagridwidget-tr-label').remove();
    $.each(
        $('#datagridwidget-tbody-arg_spec').find('tr'),
        function(idx, tr) {
            var tr_label = $('<td>')
                            .addClass('eea-sparql-datagridwidget-tr-label')
                            .text('Argument #' + (idx + 1).toString());
            $(tr).prepend(tr_label);
        }
    );
  }

  function setColumnClasses() {
    $('[name="arg_spec.name:records"]')
        .closest('td').addClass('datagridwidget-column-1');
    $('[name="arg_spec.query:records"]')
        .closest('td').addClass('datagridwidget-column-2');
    setDataGridWidgetTRLabels();
    $(document).trigger('eea-wizard-changed');

  }

  $('.datagridwidget-add-button').text('Add new argument');
  $('.datagridwidget-add-button').addClass('datagridwidget-sparql-add-button');
  $('.datagridwidget-sparql-add-button').removeClass('datagridwidget-add-button');

  $(document)
    .delegate('.datagridwidget-manipulator img', 'click', setColumnClasses);
  $(document)
    .delegate('.datagridwidget-sparql-add-button', 'click', setColumnClasses);
  setDataGridWidgetTRLabels();

});

Browser.onUploadComplete = function() {
    // don't reload the page after uploading file
};
