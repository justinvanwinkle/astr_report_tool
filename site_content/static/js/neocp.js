
$(document).ready(function() {
    var neocp_list = $('#neocp_list').DataTable( {
        select: {style: 'single'}
    });

    $('#neocp_list tbody').on('click', 'tr', function () {
        var data = neocp_list.row(this).data();
        select_neo(data[0]);
    });

    var observatory_list = $('#observatory_list').DataTable({
        select: {style: 'single'}
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
        var val = this.value.toUpperCase();
        if($(option).filter(function(){
	    return $(this).val() === val;
	}).length) {
	    select_neo(val);
        }

    });
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
    $('#neo_name').val(temporary_designation);

    // Select in list

    refresh_image();
    console.log('Selecting: ' + temporary_designation);
}

function refresh_image() {
    var data = {};
    data['longitude'] = $('#observatory_longitude').val();
    data['latitude'] = $('#observatory_latitude').val();
    data['obj'] = $('#neo_name').val();

    var jqxhr = $.post( '/ajax_object_track', data, function(res) {
        $('#track_image').attr('src', res['graphic']);
        console.log('updated image');
    });
}
