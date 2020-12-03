//Util

import { GuiState } from './guistate.js';

var Util = {
    build_method_name : function(name, cmsix) {
        var methodname = name + " ( " + cmsix + " )";
        return methodname;
    },

    append_text_to_node : function(node, txt) {
        var text_node = document.createTextNode(txt);
        node.appendChild(text_node);
    },

    add_table_borderless : function(txt, row) {
        var dnode = document.createElement('td');
        var text_node = document.createTextNode(txt);
        dnode.appendChild(text_node);
        row.appendChild(dnode);
        dnode.style.border = "0px";

        return dnode;
    },

    add_table_data_with_link : function(txt,row,linktxt) {
        var node = document.createElement('td');
        var link = document.createElement('a');
        link.setAttribute('href',linktxt);
        link.setAttribute('target','_blank');
        link.textContent = txt;
        node.appendChild(link);
        row.appendChild(node);

        return node
    },

    //add_table_data_with_link_mouseover : function(txt, row, linktxt) {
    //    var node = document.createElement('td');
    //    var link = document.createElement('a');
    //    link.setAttribute('href',linktxt);
    //    link.setAttribute('target','_blank');
    //    link.textContent = txt;
    //    node.appendChild(link);

    //    link.addEventListener("mouseover", function() { this.classList.add('mousedover');});
    //    link.addEventListener("mouseout", function() { this.classList.remove('mousedover');});

    //    row.appendChild(node);

    //    return node
    //},

    replace_node_text_with_link: function(txt, node, linktxt) {
        var link = document.createElement('a');
        link.setAttribute('href',linktxt);
        link.setAttribute('target','_blank');
        link.textContent = txt;
        node.textContent = "";
        node.appendChild(link);

        //link.addEventListener("mouseover", function() { this.classList.add('mousedover');});
        //link.addEventListener("mouseout", function() { this.classList.remove('mousedover');});
    },

    add_table_header : function(txt,row) {
        var node = document.createElement('th');
        var button = document.createElement('button');
        button.textContent = txt;
        node.appendChild(button);
        row.appendChild(node);
    },

    add_span_table_header : function(txt,row,span) {
        var node = document.createElement('th');
        var button = document.createElement('button');
        button.textContent = txt;
        node.colSpan = span;
        node.appendChild(button);
        row.appendChild(node);
    },

    add_table_header_with_sort : function(txt,row,tablename,columnindex,sort0,sortf,reverse) {
        var node = document.createElement('th');
        var button = document.createElement('button');
        var icon=document.createElement('i');
        button.onclick = function() {
            Util.sortTable(tablename, columnindex, sort0, sortf, reverse);
        };
        button.textContent = txt;
        icon.setAttribute('class', 'fas fa-sort');
        node.appendChild(button);
        button.appendChild(icon);
        row.appendChild(node);
    },

    get_child_with_tag(node, tag){
        if (node.hasChildNodes()) {
            var children = node.children;
            for (var i = 0; i < children.length; i++) {
                if (children[i].tagName !== undefined ) {
                    if (children[i].tagName.toLowerCase() == tag.toLowerCase()) {
                        return children[i];
                    }
                }
            }
        }
    },

    get_class_link : function(cnix) {
        return "/class/" + GuiState.engagement + "/" + GuiState.project + "/" + cnix;
    },

    get_method_link : function(cmsix) {
        return "/method/" + GuiState.engagement + "/" + GuiState.project + "/" + cmsix;
    },

    get_taint_link : function(taintorigin) {
        return "/taint/" + GuiState.engagement + "/" + GuiState.project + "/" + taintorigin;
    },

    sortTable : function(tableid, columnindex, sortf0, sortf, reverse) {
        var rev = 1;
        if (reverse) { rev = -1; }
        var table = document.getElementById(tableid);
        if (table.rows.length > 500) {
            alert('Current sort implementation is inefficient; sorting ' + table.rows.length +
                'rows would take a long time');
        } else {
            var switching = true;
            var shouldSwitch = false;
            var rows = null;
            while (switching) {
                switching = false;
                rows = table.rows;
                for (var i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    var x = rows[i].getElementsByTagName('td')[columnindex];
                    var y = rows[i+1].getElementsByTagName('td')[columnindex];
                    var cmp1 = sortf(x,y) * rev;
                    if (cmp1 == 0) {
                        var a1 = rows[i].getElementsByTagName('td')[0];
                        var a2 = rows[i+1].getElementsByTagName('td')[0];
                        var cmp2 = sortf0(a1,a2) * rev;
                        if (cmp2 == 1) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (cmp1 == 1) {
                        shouldSwitch = true;
                        break;
                    }
                }
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
                    switching = true;
                }
            }
        }
    },

    compareInt : function(x,y) {
        var x = x.textContent;
        var y = y.textContent;
        if (!x) return -1;
        if (!y) return 1;
        if (x == y) return 0;
        var a1 = parseInt(x);
        var a2 = parseInt(y);
        if (a1 == a2) return 0;
        if (a1 > a2) return 1;
        return -1;
    }
}

export { Util };
