3
$(document).ready(function() {
    var neocp_list = $('#neocp_list').DataTable( {
        select: {
            style: 'single'
        }

    } );

    var observatory_list = $('#observatory_list').DataTable( {
        select: {
            style: 'single'
        }
    } );

    neocp_list.on( 'select', function ( e, dt, type, indexes ) {
        if ( type === 'row' ) {
            var obj_name = neocp_list.rows(indexes).data().pluck(0);
        }
    } );

    $('#map_link').click(function() {
        latitude =  $('#observatory_latitude').val();
        longitude = $('#observatory_longitude').val();
        url = 'https://maps.google.com/?ll=' + latitude + ',' + longitude;
        window.open(url,'_blank');
    });
    load_location();
});

function fill_location_form(location) {
    var coords = location.coords;
    $('#observatory_latitude').val(coords.latitude);
    $('#observatory_longitude').val(coords.longitude);
    $('#observatory_location_accuracy').val(coords.accuracy);
}


function load_location() {
    navigator.geolocation.getCurrentPosition(
        fill_location_form, alert, {enableHighAccuracy: true});
}

function select_neo(temporary_designation) {
    // Fill text box

    // Select in list

    // refresh images and data
}
