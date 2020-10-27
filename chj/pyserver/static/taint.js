"use strict";

import { GraphUtil } from './graphutil.js';
import { Util } from './util.js';

var navselected = 'Bytecode';

var navengagement = null;
var navproject = null;
var cmsix = null;

function loadtaint() {
    show_overlay()

    var sink = document.getElementById("tsink").value;
    var loops = document.getElementById("loopsbox").checked;
    var formData = new FormData();
    if(sink !== '') {formData.append("sinkid", sink);}
    if(loops === true) {formData.append("loops", loops);}

    var url = "/taint/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
                GraphUtil.addsvg(response['content'])
            } else {
                alert('Error');
            }
        } else {
            alert('Server error');
        }
        hide_overlay();
    };
    request.open("POST", url);
    request.send(formData);
}

//function add_links() {
//    var nodes = document.getElementsByClassName('node');
//    for (var i = 0; i < nodes.length; i++) {
//        if (nodes[i].hasAttribute('cmsix')) {
//            nodes[i].addEventListener('click', function() {
//                var tgtcmsix = parseInt(this.getAttribute('cmsix'), 10);
//                window.open("/method/" + navengagement + "/" + navproject + "/" + tgtcmsix);
//            });
//            var textnode = nodes[i].getElementsByTagName('text')[0];
//            textnode.setAttribute('fill', 'blue');
//            textnode.classList.add('link');
//        }
//    }
//}

function collapse() {
    document.getElementById('sidebar').classList.toggle('collapsed');

    document.getElementById('container').classList.toggle('dataview');
    document.getElementById('container').classList.toggle('fullview');
}

function hide_overlay() {
    var overlay = document.getElementById('overlay');
    overlay.classList.remove('cgridarea');
    overlay.classList.add('hidden');
}

function show_overlay() {
    var overlay = document.getElementById('overlay');
    overlay.classList.remove('hidden');
    overlay.classList.add('cgridarea');
}

function initialize() {
    var datapage = document.getElementById('datapage');

    var data = document.getElementById('data');
    var graph = Util.get_child_with_tag(data, 'svg');
    GraphUtil.scale_graph(graph); 

    var zoomin = document.getElementById('zoomin');
    zoomin.addEventListener('click', function() {GraphUtil.zoom_in_graph()});

    var zoomout = document.getElementById('zoomout');
    zoomout.addEventListener('click', function() {GraphUtil.zoom_out_graph()});

    var gbsearch = document.getElementById('gbsearch');
    gbsearch.addEventListener('click', function() {GraphUtil.add_highlights()});

    var loopbox = document.getElementById('loopsbox');
    loopbox.addEventListener('change', function() {loadtaint()});

    var sinkbox = document.getElementById('btsink');
    sinkbox.addEventListener('click', function() {loadtaint()});

    var bcollapse = document.getElementById('options-collapse');
    bcollapse.addEventListener('click', function() {collapse()});

    datapage.addEventListener('mousedown', function() {GraphUtil.drag_element(event)});
}

initialize();

navengagement = document.getElementById('mainpage').getAttribute('eng');
navproject = document.getElementById('mainpage').getAttribute('proj');
cmsix = document.getElementById('mainpage').getAttribute('index');
