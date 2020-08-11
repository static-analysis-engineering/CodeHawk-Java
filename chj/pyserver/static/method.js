"use strict";

var navselected = 'Bytecode';
//var navengagement = document.getElementById('mainpage').getAttribute('eng');
//var navproject = document.getElementById('mainpage').getAttribute('proj');
//var cmsix = document.getElementById('mainpage').getAttribute('cmsix');

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

function addsvg(response) {
    var datapage = document.getElementById('datapage');
    var prdata = document.getElementById('data');

    datapage.classList.add('graphview');

    var new_svg_data = get_svg_data(response['svg']);

    datapage.replaceChild(new_svg_data, prdata);

    //If graph is wider than can be displayed, automatically shrink the graph;
    var datawidth = datapage.offsetWidth;
    var svgwidth = new_svg_data.scrollWidth;
    if (svgwidth > datawidth) {
        var scale = datawidth / svgwidth;
        if (scale < 0.4) {scale = 0.4;}
        var transform = build_scale_string(scale);
        data.style.transform = transform;
        data.style.transformOrigin = '0% 0% 0px';
    }

    datapage.addEventListener('mousedown', function() {drag_element(event)});
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

function build_scale_string(scale) {
    var data = document.getElementById('data');
    if (data.hasAttribute('trX') && data.hasAttribute('trY')) {
        var trX = data.getAttribute('trX');
        var trY = data.getAttribute('trY');
        return build_transform_string(trX, trY, scale);
    } else {
        data.setAttribute('scale', scale);
        var transform = 'scale(' + scale + ',' + scale + ')';
        return transform;
    }
}

function build_translate_string(trX, trY) {
    var data = document.getElementById('data');
    if (data.hasAttribute('scale')) {
        var scale = data.getAttribute('scale');
        return build_transform_string(trX, trY, scale);
    } else {
        data.setAttribute('trX', trX);
        data.setAttribute('trY', trY);
        var transform = 'translate(' + trX + 'px,' + trY + 'px)';
        return transform
    }
}

function build_transform_string(trX, trY, scale) {
    var data = document.getElementById('data');
    data.setAttribute('scale', scale);
    data.setAttribute('trX', trX);
    data.setAttribute('trY', trY);
    var transform = 'translate(' + trX + 'px,' + trY + 'px) scale(' + scale + ',' + scale + ')';
    return transform;
}

function drag_element(event) {
    document.onmousemove = move_element;
    document.onmouseup = stop_move;

    mouseX = event.clientX;
    mouseY = event.clientY;
}

function move_element(event) {
    var trX = event.clientX - mouseX;
    var trY = event.clientY - mouseY;

    mouseX = event.clientX;
    mouseY = event.clientY;

    var data = document.getElementById('data');
    if (data.hasAttribute('trX') && data.hasAttribute('trY')) {
        var curX = parseInt(data.getAttribute('trX'), 10);
        var curY = parseInt(data.getAttribute('trY'), 10);
        trX = trX + curX;
        trY = trY + curY;
    }

    var transform = build_translate_string(trX.toString(), trY.toString());
    data.style.transform = transform;
}

//When mouse is released, page elements should no longer move
function stop_move(event) {
    document.onmousemove = null;
    document.onmouseup = null;
}

function zoom_out_graph() {
    var data = document.getElementById('data');
    var zoomstr = '0.9';
    if (data.hasAttribute('scale')) {
        var zoom = parseFloat(data.getAttribute('scale'), 10);
        if (zoom > 0.1) {
            zoom = zoom - 0.1;
        }
        var zoomstr = zoom.toString();
    }
    data.setAttribute('scale', zoomstr);

    var new_scale = build_scale_string(zoomstr);
    data.style.transform = new_scale;
    data.style.webkitTransform = new_scale;
    data.style.MozTransform = new_scale;
}

function zoom_in_graph() {
    var data = document.getElementById('data');
    var zoomstr = '1.1';
    if (data.hasAttribute('scale')) {
        var zoom = parseFloat(data.getAttribute('scale'), 10);
        if (zoom < 2.0) {
            zoom = zoom + 0.1;
        }
        var zoomstr = zoom.toString();
    }
    data.setAttribute('scale', zoomstr);

    var new_scale = build_scale_string(zoomstr);
    data.style.transform = new_scale;
    data.style.webkitTransform = new_scale;
    data.style.MozTransform = new_scale;

}

function zoom_on_scroll(event) {
    var data = document.getElementById('data');
    var zoomstr = '1.0';
    if (data.hasAttribute('scale')) {
        var delta = event.deltaY;
        var zoom = parseFloat(data.getAttribute('scale'), 10) + (delta / 100);
        if (zoom < 0.1) { zoom = 1.0; }
        if (zoom > 2.0) { zoom = 2.0; }
        var zoomstr = zoom.toString();
        data.setAttribute('scale', zoomstr);
    } else {
        data.setAttribute('scale', zoomstr);
    }
    data.style.transform = 'scale(' + zoomstr + ',' + zoomstr + ')';
    //data.style.transformOrigin = '0% 0%';
}

function initialize() {
    hide_graph_aux();

    var datapage = document.getElementById('datapage');
    //datapage.addEventListener('wheel', function() {zoom_on_scroll(event)});

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

add_nav_listener('Bytecode');
add_nav_listener('CFG');
add_nav_listener('CFG+COST');
add_nav_listener('CG');
add_nav_listener('REVCG');
