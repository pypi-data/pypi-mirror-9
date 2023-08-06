/**
 # Copyright (c) 2013 Riverbed Technology, Inc.
 #
 # This software is licensed under the terms and conditions of the
 # MIT License set forth at:
 #   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
 # This software is distributed "AS IS" as set forth in the License.
 */

rvbd.widgets.maps = {};

rvbd.widgets.maps.MapWidget = function(postUrl, isEmbedded, div, id, slug, options, criteria) {
    rvbd.widgets.Widget.apply(this, [postUrl, isEmbedded, div, id, slug, options, criteria]);
};
rvbd.widgets.maps.MapWidget.prototype = Object.create(rvbd.widgets.Widget.prototype)

rvbd.widgets.maps.MapWidget.prototype.render = function(data) {
    var self = this;

    var $div = $(self.div);

    self.titleMsg = data['chartTitle'];
    self.buildInnerLayout();

    $(self.content)
        .height($div.height() - 52);

    var bounds,
        mapOptions = {
            zoom: 3,
            center: new google.maps.LatLng(42.3583, -71.063),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };

    var map = new google.maps.Map(self.content, mapOptions);

    if (data.minbounds) {
        bounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(data.minbounds[0][0], data.minbounds[0][1]),
            new google.maps.LatLng(data.minbounds[1][0], data.minbounds[1][1])
        );
    } else {
        bounds = new google.maps.LatLngBounds();
    }

    var valStr, title, marker;
    $.each(data.circles, function(i,c) {
        c.map = map;
        c.center = new google.maps.LatLng(c.center[0], c.center[1]);
        bounds.extend(c.center)

        valStr = (c.formatter ? rvbd.formatters[c.formatter](c.value, 2)
                              : c.value) + c.units;
        title = c.title + '\n' + valStr;


        marker = new google.maps.Marker({
            position: c.center,
            map: map,
            title: title,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: c.size,
                strokeColor: "red",
                strokeOpacity: 0.8,
                strokeWeight: 0.5,
                fillOpacity: 0.35,
                fillColor: "red"
            }
        });
    });
    map.fitBounds(bounds);
}
