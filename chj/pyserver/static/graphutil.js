"use strict";

var GraphUtil = {
    mouseX : null,
    mouseY : null,

    add_highlights : function() {
        var searchvalue = document.getElementById('gsearch').value;

        var nodes = document.getElementsByClassName('node');
        for (var i = 0; i < nodes.length; i++) {
            nodes[i].removeAttribute('opacity');
        }

        if (searchvalue.length == 0) {
            return;
        }

        for (var i = 0; i < nodes.length; i++) {
            var textnode = nodes[i].getElementsByTagName('text')[0];

            if (!(textnode.textContent.includes(searchvalue))) {
                nodes[i].setAttribute('opacity', '0.3');
            }
        }
    },

    addsvg : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('data');

        datapage.classList.add('graphview');

        var new_svg_data = GraphUtil.get_svg_data(response['svg']);
        datapage.replaceChild(new_svg_data, prdata);
        GraphUtil.scale_graph(new_svg_data);
        datapage.addEventListener('mousedown', function() {GraphUtil.drag_element(event)});
    },

    scale_graph : function(svg) {
        var datapage = document.getElementById('datapage');

        var datawidth = datapage.offsetWidth;
        var svgwidth = svg.scrollWidth;
        if (svgwidth > datawidth) {
            var scale = datawidth / svgwidth;
            if (scale < 0.4) { scale = 0.4; } //Beyond this the graph is too small to read
            var transform = GraphUtil.build_scale_string(scale);
            data.style.transform = transform;
            data.style.transformOrigin = '0% 0% 0px';
        }
    },

    build_scale_string : function(scale) {
        var data = document.getElementById('data');
        if (data.hasAttribute('trX') && data.hasAttribute('trY')) {
            var trX = data.getAttribute('trX');
            var trY = data.getAttribute('trY');
            return GraphUtil.build_transform_string(trX, trY, scale);
        } else {
            data.setAttribute('scale', scale);
            var transform = 'scale(' + scale + ',' + scale + ')';
            return transform;
        }
    },

    build_translate_string : function(trX, trY) {
        var data = document.getElementById('data');
        if (data.hasAttribute('scale')) {
            var scale = data.getAttribute('scale');
            return GraphUtil.build_transform_string(trX, trY, scale);
        } else {
            data.setAttribute('trX', trX);
            data.setAttribute('trY', trY);
            var transform = 'translate(' + trX + 'px,' + trY + 'px)';
            return transform
        }
    },

    build_transform_string : function(trX, trY, scale) {
        var data = document.getElementById('data');
        data.setAttribute('scale', scale);
        data.setAttribute('trX', trX);
        data.setAttribute('trY', trY);
        var transform = 'translate(' + trX + 'px,' + trY + 'px) scale(' + scale + ',' + scale + ')';
        return transform;
    },

    drag_element : function(event) {
        document.onmousemove = GraphUtil.move_element;
        document.onmouseup = GraphUtil.stop_move;

        GraphUtil.mouseX = event.clientX;
        GraphUtil.mouseY = event.clientY;
    },

    move_element : function(event) {
        var trX = event.clientX - GraphUtil.mouseX;
        var trY = event.clientY - GraphUtil.mouseY;

        GraphUtil.mouseX = event.clientX;
        GraphUtil.mouseY = event.clientY;

        var data = document.getElementById('data');
        if (data.hasAttribute('trX') && data.hasAttribute('trY')) {
            var curX = parseInt(data.getAttribute('trX'), 10);
            var curY = parseInt(data.getAttribute('trY'), 10);
            trX = trX + curX;
            trY = trY + curY;
        }

        var transform = GraphUtil.build_translate_string(trX.toString(), trY.toString());
        data.style.transform = transform;
    },   

    get_svg_data : function(response) {
        var svg = response;

        var new_svg_data = document.createElement('div');
        new_svg_data.setAttribute('id', 'data');

        new_svg_data.innerHTML = response;

        return new_svg_data;
    },

    //When mouse is released, page elements should no longer move
    stop_move : function(event) {
        document.onmousemove = null;
        document.onmouseup = null;
    },

    zoom_out_graph : function() {
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

        var new_scale = GraphUtil.build_scale_string(zoomstr);
        data.style.transform = new_scale;
        data.style.webkitTransform = new_scale;
        data.style.MozTransform = new_scale;
    },

    zoom_in_graph : function() {
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

        var new_scale = GraphUtil.build_scale_string(zoomstr);
        data.style.transform = new_scale;
        data.style.webkitTransform = new_scale;
        data.style.MozTransform = new_scale;
    }
}

export { GraphUtil };
