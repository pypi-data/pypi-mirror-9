$(document).ready(function() {
    $('#btn').click(function() {

        start = $(".object").length;
        end = start + parseInt($('#next').val(), 10);

        // Create URL
        var url = '/lazyloader/lazyloader-demoobject-html-' + start + '-' + end + '/';
        console.log(url);
        var request = $.get(url, {
            // Get parameters
            "column": "stock",
            "search_value": true
        }, function (data) {
            // Add fetched data to the container
            $("#container").append(data);
        });

    });
});