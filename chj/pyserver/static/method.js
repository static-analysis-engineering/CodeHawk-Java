"use strict";

import { GraphUtil } from './graphutil.js';

var navselected = 'Bytecode';

var navengagement = null;
var navproject = null;
var cmsix = null;

var mouseX = null;
var mouseY = null;

function loadcfg(navengagement, navproject, cmsix) {
    var url = "/methodcfg/" + navengagement + "/" + navproject + "/" + cmsix;
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
    };
    request.open("GET", url);
    request.send();
}

function loadcfgcost(navengagement, navproject, cmsix) {
    var url = "/methodcfgcost/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            GraphUtil.addsvg(response['content']);
        } else {
            alert('Error');
        }
    } else {
        alert('Server error');
    }
    };
    request.open("GET", url);
    request.send();
}

function loadsimplecfgcost(navengagement, navproject, cmsix) {
    var url = "/methodsimplecfgcost/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            GraphUtil.addsvg(response['content']);
        } else {
            alert('Error');
        }
    } else {
        alert('Server error');
    }
    };
    request.open("GET", url);
    request.send();
}

function loadcg(navengagement, navproject, cmsix) {
    var url = "/methodcg/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            GraphUtil.addsvg(response['content']);
            add_links();
        } else {
            alert('Error');
        }
    } else {
        alert('Server error');
    }
    };
    request.open("GET", url);
    request.send();
}

function loadrevcg(navengagement, navproject, cmsix) {
    var url = "/methodrevcg/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            GraphUtil.addsvg(response['content']);
        } else {
            alert('Error');
        }
    } else {
        alert('Server Error');
    }
    };
    request.open("GET", url);
    request.send();
}

function hide_graph_aux() {
    document.getElementById('zoomin').classList.add('hidden');
    document.getElementById('zoomout').classList.add('hidden');
    document.getElementById('options-collapse').classList.add('hidden');
    document.getElementById('sidebar').classList.add('hidden');

    var container = document.getElementById('container');
    container.removeAttribute('class');
    container.setAttribute('class', 'simpleview');
}

function show_graph_aux() {
    document.getElementById('zoomin').classList.remove('hidden');
    document.getElementById('zoomout').classList.remove('hidden');
    document.getElementById('options-collapse').classList.remove('hidden');
    document.getElementById('sidebar').classList.remove('hidden');

    var container = document.getElementById('container');
    container.removeAttribute('class');
    container.setAttribute('class', 'dataview');
}

function select_nav(navitem) {
    if (navselected) {
        document.getElementById(navselected).classList.remove('selected')
    }

    var next = document.getElementById(navitem);
    next.classList.add('class', 'selected');

    navselected = navitem;

    if (navselected == 'Bytecode') {
        //loadmethodbytecode(navengagement, navproject, cmsix);
        hide_graph_aux();
    }
    else if (navselected == 'CFG') {
        loadcfg(navengagement, navproject, cmsix);
        show_graph_aux();
    }
    else if (navselected == 'CFG+COST') {
        loadcfgcost(navengagement, navproject, cmsix);
        show_graph_aux();
    }
    else if (navselected == 'CG') {
        loadcg(navengagement, navproject, cmsix);
        show_graph_aux();
    }
    else if (navselected == 'REVCG') {
        loadrevcg(navengagement, navproject, cmsix);
        show_graph_aux();
    }
}

function add_nav_listener(tag) {
    document.getElementById(tag).addEventListener('click', function() {select_nav(tag)})
}

function switch_costs() {
    if (navselected == 'CFG+COST') {
        if (scostsbox.checked == true) {
            loadsimplecfgcost(navengagement, navproject, cmsix);
        } else {
            loadcfgcost(navengagement, navproject, cmsix);
        }    
    }
}

function color_nodes() {
    reset_fill();

    var nodes = document.getElementsByClassName('node');  
    var loopbox = document.getElementById('loopsbox');
    if (loopbox.checked == true) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].hasAttribute('ldepth')) {
                var ldepth = parseInt(nodes[i].getAttribute('ldepth'), 10);
                var polygon = nodes[i].getElementsByTagName('polygon')[0];
                if (ldepth == 1) {
                    polygon.setAttribute('fill', '#FF8888');
                }
                if (ldepth == 2) {
                    polygon.setAttribute('fill', '#FF4444');
                }
                if (ldepth >= 3) {
                    polygon.setAttribute('fill', '#FF0000');
                }
            }
        }
    } else {
        for (var i = 0; i < nodes.length; i++) {
            var polygon = nodes[i].getElementsByTagName('polygon')[0];
            polygon.setAttribute('fill', '#f4f4f4');
        }
    }
}

function add_links() {
    var nodes = document.getElementsByClassName('node');
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].hasAttribute('cmsix')) {
            nodes[i].addEventListener('click', function() {
                var tgtcmsix = parseInt(this.getAttribute('cmsix'), 10);
                window.open("/method/" + navengagement + "/" + navproject + "/" + tgtcmsix);
            });
            var textnode = nodes[i].getElementsByTagName('text')[0];
            textnode.setAttribute('fill', 'blue');
            textnode.classList.add('link');
        }
    }
}

function reset_fill() {
    var nodes = document.getElementsByClassName('node');
    for (var i = 0; i < nodes.length; i++) {
        var polygon = nodes[i].getElementsByTagName('polygon')[0];
        polygon.setAttribute('fill', '#f4f4f4');
    }
}

function collapse() {
    document.getElementById('sidebar').classList.toggle('collapsed');

    document.getElementById('container').classList.toggle('dataview');
    document.getElementById('container').classList.toggle('fullview');
}

function initialize() {
    hide_graph_aux();

    var datapage = document.getElementById('datapage');

    var zoomin = document.getElementById('zoomin');
    zoomin.addEventListener('click', function() {GraphUtil.zoom_in_graph()});

    var zoomout = document.getElementById('zoomout');
    zoomout.addEventListener('click', function() {GraphUtil.zoom_out_graph()});

    var gbsearch = document.getElementById('gbsearch');
    gbsearch.addEventListener('click', function() {GraphUtil.add_highlights()});

    var loopbox = document.getElementById('loopsbox');
    loopbox.addEventListener('change', function() {color_nodes()});

    var costbox = document.getElementById('scostsbox');
    costbox.addEventListener('change', function() {switch_costs()});

    var bcollapse = document.getElementById('options-collapse');
    bcollapse.addEventListener('click', function() {collapse()});
}

initialize();

navengagement = document.getElementById('mainpage').getAttribute('eng');
navproject = document.getElementById('mainpage').getAttribute('proj');
cmsix = document.getElementById('mainpage').getAttribute('index');

add_nav_listener('Bytecode');
add_nav_listener('CFG');
add_nav_listener('CFG+COST');
add_nav_listener('CG');
add_nav_listener('REVCG');
