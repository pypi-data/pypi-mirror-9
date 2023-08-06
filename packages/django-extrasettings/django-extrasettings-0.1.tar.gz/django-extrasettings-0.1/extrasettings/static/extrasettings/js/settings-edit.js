$(function () {
    if ($('#id_settings').length > 0) {
        var editor;

        $('#id_settings')
            .add($('.form-row.field-schema'))
            .add($('.deletelink-box'))
            .add($('input[name="_addanother"]'))
            .hide();

        $('#id_settings').after('<div id="id_settings_json"></div>');
        $('#id_settings_json').css({
            'margin-left': '95px'
        });

        editor = new JSONEditor($('#id_settings_json').get(0), {
            schema:              JSON.parse($('#id_schema').val()),
            startval:            JSON.parse($('#id_settings').val()),
            theme:               'bootstrap3',
            required_by_default: true
        });


        $('form#extrasetting_form').on('submit', function () {
            $('#id_settings').val(JSON.stringify(editor.getValue()));
        });

    } else {
        $('.actions')
            .add($('.action-checkbox-column'))
            .add($('.object-tools'))
            .add($('.action-checkbox'))
            .hide();
    }
});