"use strict";

import { MethodBytecode } from './methodbytecode.js';

var navselected = 'Bytecode';
//var navengagement = document.getElementById('mainpage').getAttribute('eng');
//var navproject = document.getElementById('mainpage').getAttribute('proj');
//var cmsix = document.getElementById('mainpage').getAttribute('cmsix');

var navengagement = null;
var navproject = null;
var cmsix = null;

function loadcfg(navengagement, navproject, cmsix) {
    var url = "/methodcfg/" + navengagement + "/" + navproject + "/" + cmsix;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            addsvg(response['content'])
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
            addsvg(response['content']);
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
            addsvg(response['content']);
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
            addsvg(response['content']);
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
            addsvg(response['content']);
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

function select_nav(navitem) {
    if (navselected) {
        document.getElementById(navselected).classList.remove('selected')
    }

    var next = document.getElementById(navitem);
    next.classList.add('class', 'selected');

    navselected = navitem;

    if (navselected == 'Bytecode') {
        MethodBytecode.loadmethodbytecode(navengagement, navproject, cmsix);
    }
    else if (navselected == 'CFG') {
        loadcfg(navengagement, navproject, cmsix);
    }
    else if (navselected == 'CFG+COST') {
        loadcfgcost(navengagement, navproject, cmsix);
    }
    else if (navselected == 'CG') {
        loadcg(navengagement, navproject, cmsix);
    }
    else if (navselected == 'REVCG') {
        loadrevcg(navengagement, navproject, cmsix);
    }
}

function addsvg(response) {
    var datapage = document.getElementById('datapage');
    var prdata = document.getElementById('data');

    var new_svg_data = get_svg_data(response['svg']);

    datapage.replaceChild(new_svg_data, prdata);
}

function get_svg_data(response) {
    var svg = response;

    var new_svg_data = document.createElement('div');
    new_svg_data.setAttribute('id', 'data');

    new_svg_data.innerHTML = response;

    return new_svg_data;
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

function search_nodes() {
    reset_fill();

    var searchvalue = document.getElementById('gsearch').value;
    if (searchvalue.length == 0) {return;}

    var nodes = document.getElementsByClassName('node');
    for (var i = 0; i < nodes.length; i++) {
        var textnode = nodes[i].getElementsByTagName('text')[0];
        if (textnode.textContent.includes(searchvalue)) {
            var polygon = nodes[i].getElementsByTagName('polygon')[0];
            polygon.setAttribute('fill', '#FF0000');
        }
    }
}

function add_links() {
    var nodes = document.getElementsByClassName('node');
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].hasAttribute('cmsix')) {
            nodes[i].addEventListener('click', function() {
                var tgtcmsix = parseInt(this.getAttribute('cmsix'), 10);
                window.open("/methodbytecode/" + navengagement + "/" + navproject + "/" + tgtcmsix);
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
    var collapsed = document.getElementById('sidebar').classList.toggle('collapsed');
    if (collapsed == true) {
        document.getElementById('datapage').style.width = '98%';
    } else {
        document.getElementById('datapage').style.width = '80%';
    }
}

function zoom_out_graph() {
    var data = document.getElementById('data');
    var zoomstr = '90';
    if (data.hasAttribute('zoom')) {
        var zoom = parseInt(data.getAttribute('zoom'), 10);
        if (zoom > 10) {
            zoom = zoom - 10;
        }
        var zoomstr = zoom.toString();
    }
    data.setAttribute('zoom', zoomstr);
    data.style.transform = 'scale(' + zoomstr + '%,' + zoomstr + '%)';
    data.style.transformOrigin = '50% 50%';
}

function zoom_in_graph() {
    var data = document.getElementById('data');
    var zoomstr = '110';
    if (data.hasAttribute('zoom')) {
        var zoom = parseInt(data.getAttribute('zoom'), 10);
        if (zoom < 200) {
            zoom = zoom + 10;
        }
        var zoomstr = zoom.toString();
    }
    data.setAttribute('zoom', zoomstr);
    data.style.transform = 'scale(' + zoomstr + '%,' + zoomstr + '%)';
    data.style.transformOrigin = '0% 0%';
}

function zoom_on_scroll(event) {
    var data = document.getElementById('data');
    var zoomstr = '100';
    if (data.hasAttribute('zoom')) {
        var delta = event.deltaY;
        var zoom = parseInt(data.getAttribute('zoom'), 10) + delta;
        if (zoom < 10) { zoom = 10; }
        if (zoom > 200) { zoom = 200; }
        var zoomstr = zoom.toString();
        data.setAttribute('zoom', zoomstr);
    } else {
        data.setAttribute('zoom', zoomstr);
    }
    data.style.transform = 'scale(' + zoomstr + '%,' + zoomstr + '%)';
    data.style.transformOrigin = '0% 0%';
}

function initialize() {
    var datapage = document.getElementById('datapage');
    datapage.addEventListener('wheel', function() {zoom_on_scroll(event)});

    var zoomin = document.getElementById('zoomin');
    zoomin.addEventListener('click', function() {zoom_in_graph()});

    var zoomout = document.getElementById('zoomout');
    zoomout.addEventListener('click', function() {zoom_out_graph()});

    var gbsearch = document.getElementById('gbsearch');
    gbsearch.addEventListener('click', function() {search_nodes()});

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

add_nav_listener('CFG');
add_nav_listener('CFG+COST');
add_nav_listener('CG');
add_nav_listener('REVCG');
