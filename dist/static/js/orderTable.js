var editor;
$(document).ready(function() {
    $(function () {
                $('#datetimepicker1').datetimepicker({
                    locale: 'en'
                });
            });

    var table = $('#dataTable').DataTable( );







    //make status editable
    $('#status').editable({
        type: 'select',
        title: 'Select status',
        placement: 'right',
        value: 2,
        source: [
            {value: 1, text: 'status 1'},
            {value: 2, text: 'status 2'},
            {value: 3, text: 'status 3'}
        ]
        ,pk: 1
        ,url: '/post'


    });

    });

