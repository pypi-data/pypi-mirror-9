.. contents::

==========================================================================
collective.geo.leaflet
==========================================================================

This package use the collective.geo.* suite with leaflet.


Todo
====

[ ] Get "attribution" map from registry or 

[ ] Testing loading map with Robot

[ ] Add uninstall profile

[ ] Translations

[ ] Simple element view should use geojson

[ ] Use leaflet for control panel map

[ ] Use leaflet for configure map

Dependencies
============

- collective.geo.behaviour
- collective.geo.contentlocations
- collective.geo.geographer
- collective.geo.json
- collective.geo.mapwidget
- collective.geo.openlayers
- collective.geo.settings
- collective.js.leaflet
- collective.z3cform.mapwidget
- collective.z3cform.colorpicker

How to add baseLayer
====================

What is a leaflet baseLayer :
http://leafletjs.com/examples/layers-control.html


In Plone, if you want to add a baseLayer, you have to add a subscriber on collective.geo.geographer.interfaces.IGeoreferenced (for exemple, in `configure.zcml`)::

    <subscriber
        for="collective.geo.geographer.interfaces.IGeoreferenced"
        provides="collective.geo.leaflet.interfaces.IMapLayer"
        factory=".maplayers.OpenStreetMap
        />

After, create your factory in python (`maplayers.py`)::

    from collective.geo.leaflet.maplayers import MapLayer
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    
    
    class OpenStreetMap(MapLayer):
        name = u"osm"
        title = _(u"Open Street Map")
        index = ViewPageTemplateFile('browser/layers/osm.pt')

And add your javascript into a template file `osm.pt`::

    <script type="text/javascript">
        var osmAttrib = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';
        var osmUrl = 'http://{s}.tile.osm.org/{z}/{x}/{y}.png';
        var %(name)s = L.tileLayer(osmUrl, {
             attribution: osmAttrib,
        });
    </script>


Tests
=====

This package is tested using Travis CI. The current status is :

.. image:: https://travis-ci.org/collective/collective.geo.leaflet.svg
    :target: https://travis-ci.org/collective/collective.geo.leaflet
