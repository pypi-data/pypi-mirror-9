baselayers = {};
overlays = {};
layers = $('div.baselayers').data('baselayers');
for (var layer in layers) {
    baselayers[layers[layer].title] = eval(layers[layer].name);
}
map.addLayer(eval(layers[0].name));
controllayers = L.control.layers(baselayers).addTo(map)
if ($('#geojson_url').length > 0) {
    //var markers = new L.MarkerClusterGroup();
    urls = $('#geojson_url').data('geojson_url');
    var geojsons = [];
    for (u in urls) {
        url = urls[u];
        var layername;
        $.getJSON(url, function(data) {
            layername = data.title;
            geojson = L.geoJson(data, {
                onEachFeature: function (feature, layer) {
                    layer.bindPopup(
                        '<a href="'+feature.properties.url+'" target="_blank">'+
                        '<h3>'+feature.properties.title+'</h3>'+
                        '</a>'+
                        '<p>'+feature.properties.description+'</p>');
                },
                pointToLayer: function (feature, latlng) {
                    //Extend the Default marker class
                    var CustomIcon = L.Icon.Default.extend({
                        options: {
                            iconUrl: feature.style.image
                        }
                    });
                    var customIcon = new CustomIcon();
                    return L.marker(latlng, {icon: customIcon});
                }
            });
            //markers.addLayer(geojson);
            //map.addLayer(markers);
            map.addLayer(geojson);
            controllayers.addOverlay(geojson, layername);
            //overlays[layername] = geojson;
        });
    }
}
