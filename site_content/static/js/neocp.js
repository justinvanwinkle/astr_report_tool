
$(document).ready(function() {
    $('#neocp_list').DataTable( {
        select: true
    } );
    $('#observatory_list').DataTable( {
        select: true
    } );
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
