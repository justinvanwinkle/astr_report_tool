
log = console.log;

$(document).ready(function() {
    $('#refresh_image').click(function() {
        refresh_image();
    });

    var observatory_table = $('#observatory_list').DataTable({
        select: {style: 'single'}
    });

    observatory_table.on('select', function (e, dt, type, indexes) {
        log('obs event');
        var data = observatory_table.row(indexes).data();
        select_observatory(data[0]);
    });

    $('#map_link').click(function() {
        latitude =  $('#observatory_latitude').val();
        longitude = $('#observatory_longitude').val();
        url = 'https://maps.google.com/?ll=' + latitude + ',' + longitude;
        window.open(url,'_blank');
    });

    $("#geolocate_button").click( function() {
        load_location();
    });

    $("#neo_name").on('input', function () {
	var option = $('#neo_name_list option');
        var val = this.value;
        if($(option).filter(function(){
	    return $(this).val().toUpperCase() === val.toUpperCase();
	}).length) {
	    select_neo(val);
        }

    });

    function reload_object_list() {
        if (!$.fn.DataTable.isDataTable( '#neocp_list')) {
            $('#neocp_list')
                .dataTable({
                    'ajax': {
                        "url": "/object_list",
                        "data": function(d) {
                            d.latitude = $('#observatory_latitude').val();
                            d.longitude = $('#observatory_longitude').val();
                            d.altitude = $('#observatory_altitude').val();
                            d.obscode = $('#observatory_code').val();
                        }},
                    select: {style: 'single'}})
                .on('init.dt', function () {
                    log('loaded');
                    $('#neocp_list').DataTable()
                        .on('select', function (e, dt, type, indexes) {
                            log('click');
                            var neocp_table = $('#neocp_list').DataTable();
                            var data = neocp_table.row(indexes).data();
                            select_neo(data[0]);
                        });
                });
        } else {
            $('#neocp_list').DataTable().ajax.reload();
        }
    }

    function fill_location_form(location) {
        var coords = location.coords;
        $('#observatory_latitude').val(coords.latitude);
        $('#observatory_longitude').val(coords.longitude);
        $('#observatory_location_accuracy').val(coords.accuracy);
        reload_object_list();
    }


    function load_location() {
        navigator.geolocation.getCurrentPosition(
            fill_location_form, alert, {enableHighAccuracy: true});
    }


    function select_neo(temporary_designation) {
        $('#neo_name').val(temporary_designation);

        // Select in list

        refresh_image();
        log('Selecting: ' + temporary_designation);
    }


    function select_observatory(code) {
        $('#observatory_code').val(code);
        $('#observatory_latitude').val('');
        $('#observatory_longitude').val('');
        $('#observatory_location_accuracy').val('');
        $('#observatory_altitude').val('');

        reload_object_list();
    }


    function refresh_image() {
        var data = {
            obscode: $('#observatory_code').val(),
            latitude: $('#observatory_longitude').val(),
            longitude: $('#observatory_latitude').val(),
            altitude: $('#observatory_altitude').val(),
            obj: $('#neo_name').val(),
            sigma_high: $('#sigma_high').val(),
            sigma_low: $('#sigma_low').val(),
            cmap_name: $('#cmap_name').val()};
        log(data);

        $.post( '/ajax_object_track', data, function(res) {
            $('#track_image').attr('src', res['graphic']);
            log('updated image');
            $('#ephemeride_table').html(res['ephemeride_table']);
        });
    }

});
