/*****************************************************************************
 * FILE:    Tethys Map View Library
 * DATE:    February 4, 2015
 * AUTHOR:  Nathan Swain
 * COPYRIGHT: (c) 2015 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var TETHYS_MAP_VIEW = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	var public_interface,				// Object returned by the module
      m_default_projection,   // Spherical Mercator projection
      m_map_target,           // Selector for the map container
      m_map;					        // The map

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	var ol_base_map_init, ol_controls_init, ol_layers_init, ol_map_init, ol_view_init;


 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/

  // Initialize the background map
  ol_base_map_init = function()
  {
    // Constants
    var OPEN_STEET_MAP = 'OpenStreetMap',
        BING = 'Bing',
        MAP_QUEST = 'MapQuest';


    // Declarations
    var base_map_json,
        base_map_layer,
        base_map_obj;

    // Default base map
    base_map_layer = new ol.layer.Tile({
      source: new ol.source.OSM()
    });

    // Get control settings from data attribute
    base_map_json = $('#' + m_map_target).attr('data-base-map');

    if (typeof base_map_json !== typeof undefined && base_map_json !== false) {
      base_map_obj = JSON.parse(base_map_json);

      if (typeof base_map_obj === 'string') {
        if (base_map_obj === OPEN_STEET_MAP) {
          // Initialize default open street map layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.OSM()
          });

        } else if (base_map_obj === BING) {
          // Initialize default bing layer

        } else if (base_map_obj === MAP_QUEST) {
          // Initialize default map quest layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.MapQuest({layer: 'sat'})
          });

        }

      } else if (typeof base_map_obj === 'object') {

        if (OPEN_STEET_MAP in base_map_obj) {
          // Initialize custom open street map layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.OSM(base_map_obj[OPEN_STEET_MAP])
          });

        } else if (BING in base_map_obj) {
          // Initialize custom bing layer
          base_map_layer = new ol.layer.Tile({
            preload: Infinity,
            source: new ol.source.BingMaps(base_map_obj[BING])
          });

        } else if (MAP_QUEST in base_map_obj) {
          // Initialize custom map quest layer
          base_map_layer = new ol.layer.Tile({
            source: new ol.source.MapQuest(base_map_obj[MAP_QUEST])
          });
        }
      }
    }

    // Add the base map to layers
    m_map.addLayer(base_map_layer);
  };

  // Initialize the controls
  ol_controls_init = function()
  {
    // Constants
    var ZOOM_SLIDER = 'ZoomSlider',
        ROTATE = 'Rotate',
        ZOOM_EXTENT = 'ZoomToExtent',
        FULL_SCREEN = 'FullScreen',
        MOUSE_POSITION = 'MousePosition',
        SCALE_LINE = 'ScaleLine';

    var controls_json,
        controls_list,
        controls;

    // Get control settings from data attribute
    controls_json = $('#' + m_map_target).attr('data-controls');

    // Start with defaults
    controls = ol.control.defaults();

    if (typeof controls_json !== typeof undefined && controls_json !== false) {
      controls_list = JSON.parse(controls_json);

      for (var i = 0; i < controls_list.length; i++) {
        var current_control;

        current_control = controls_list[i];

        // Handle string case
        if (typeof current_control === 'string') {
          if (current_control === ZOOM_SLIDER) {
            m_map.addControl(new ol.control.ZoomSlider());
          }
          else if (current_control === ROTATE) {
            m_map.addControl(new ol.control.Rotate());
          }
          else if (current_control === ZOOM_EXTENT) {
            m_map.addControl(new ol.control.ZoomToExtent());
          }
          else if (current_control === FULL_SCREEN) {
            m_map.addControl(new ol.control.FullScreen());
          }
          else if (current_control === MOUSE_POSITION) {
            m_map.addControl(new ol.control.MousePosition());
          }
          else if (current_control === SCALE_LINE) {
            m_map.addControl(new ol.control.ScaleLine());
          }

        // Handle object case
        } else if (typeof current_control === 'object') {
          if (ZOOM_SLIDER in current_control){
            m_map.addControl(new ol.control.ZoomSlider(current_control[ZOOM_SLIDER]));
          }
          else if (ROTATE in current_control){
            m_map.addControl(new ol.control.Rotate(current_control[ROTATE]));
          }
          else if (FULL_SCREEN in current_control){
            m_map.addControl(new ol.control.FullScreen(current_control[FULL_SCREEN]));
          }
          else if (MOUSE_POSITION in current_control){
            m_map.addControl(new ol.control.MousePosition(current_control[MOUSE_POSITION]));
          }
          else if (SCALE_LINE in current_control){
            m_map.addControl(new ol.control.ScaleLine(current_control[SCALE_LINE]));
          }
          else if (ZOOM_EXTENT in current_control){
            var control_obj = current_control[ZOOM_EXTENT];

            // Transform coordinates to default CRS
            if ('projection' in control_obj && 'extent' in control_obj) {
              control_obj['extent'] = ol.proj.transformExtent(control_obj['extent'], control_obj['projection'], m_default_projection);
              delete control_obj['projection'];
            }
            m_map.addControl(new ol.control.ZoomToExtent(control_obj));
          }
        }
      }
    }

    return controls;

  };

  // Initialize the layers
  ol_layers_init = function()
  {
    // Constants
    var GEOJSON = 'GeoJSON',
        IMAGE_WMS = 'WMS',
        KML = 'KML',
        VECTOR = 'Vector',
        TILED_WMS = 'TiledWMS';

    var layers_json,
        layers_list;

    // Get layers for data attributes
    layers_json = $('#' + m_map_target).attr('data-layers');

    if (typeof layers_json !== typeof undefined && layers_json !== false) {
      layers_list = JSON.parse(layers_json);

      for (var i = 0; i < layers_list.length; i++) {
        var current_layer,
            layer;

        current_layer = layers_list[i];

        if (GEOJSON in current_layer) {
          layer = new ol.layer.Vector({
            source: ol.source.GeoJSON(current_layer[GEOJSON])
          });

        }
        else if (IMAGE_WMS in current_layer) {
          layer = new ol.layer.Image({
            source: new ol.source.ImageWMS(current_layer[IMAGE_WMS])
          });

        }
        else if (KML in current_layer) {
          layer = new ol.layer.Vector({
            source: new ol.source.KML(current_layer[KML])
          });

        }
        else if (VECTOR in current_layer) {

        }
        else if (TILED_WMS in current_layer) {
          layer = new ol.layer.Tile({
            source: new ol.source.TileWMS(current_layer[TILED_WMS])
          });
        }

        if (typeof layer !== typeof undefined) {
          m_map.addLayer(layer);
        }
      }
    }

    //layer = new ol.layer.Image({
    //  source: new ol.source.ImageWMS({
    //    url: 'http://192.168.59.103:8181/geoserver/wms',
    //    params: {'LAYERS': 'topp:states'},
    //    serverType: 'geoserver'
    //  })
    //});

    //m_map.addLayer(layer);

  };

  // Initialize the map
 	ol_map_init = function()
  {
    // Init Map
    m_map = new ol.Map({
      target: m_map_target,
      view: new ol.View({
        center: [0, 0],
        zoom: 2,
        minZoom: 0,
        maxZoom: 28
      })
    });

    // Init controls
    ol_controls_init();

    // Init base map
    ol_base_map_init();

    // Init layers
    ol_layers_init();

    // Init View
    ol_view_init();

  };

  // Initialize the map view
  ol_view_init = function()
  {
    // Declarations
    var view_json;

    // Get view settings from data attribute
    view_json = $('#' + m_map_target).attr('data-view');

    if (typeof view_json !== typeof undefined && view_json !== false) {
      var view_obj;

      view_obj = JSON.parse(view_json);

      if ('projection' in view_obj && 'center' in view_obj) {
        // Transform coordinates to default CRS
        view_obj['center'] = ol.proj.transform(view_obj['center'], view_obj['projection'], m_default_projection);
        delete view_obj['projection'];
      }

      m_map.setView(new ol.View(view_obj));
    }

  };

  /************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
    // Map container selector
    m_map_target = 'map_view';
    m_default_projection = 'EPSG:3857';

    // Initialize the map
    ol_map_init();

	});

	/************************************************************************
 	*                        DEFINE PUBLIC INTERFACE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 * This is the object that is returned by the library wrapper function.
	 * See below.
	 * NOTE: The functions in the public interface have access to the private
	 * functions of the library because of JavaScript function scope.
	 */
  var get_map, get_target;

  get_map = function() {
    return m_map;
  };

  get_target = function() {
    return m_map_target;
  };

  public_interface = {
    getMap: get_map,
    getTarget: get_target
  };

	return public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.