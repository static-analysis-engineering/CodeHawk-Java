"use strict";

import { GuiState } from './guistate.js';
import { Util } from './util.js';

var navselected = 'HOME';

var navengagement = null;
var navproject = null;
var cmsix = null;

function add_links() {
    var methodnodes = document.getElementsByName('method');
    var l = methodnodes.length;

    for (var i = 0; i < l; i++) {
       var methodnode = methodnodes[i];
       var cmsix = methodnode.getAttribute('cmsix');
       var linktxt = Util.get_method_link(cmsix);
       var txt = methodnode.textContent;

       Util.replace_node_text_with_link(txt, methodnode, linktxt);
    }
}

navengagement = document.getElementById('mainpage').getAttribute('eng');
navproject = document.getElementById('mainpage').getAttribute('proj');
cmsix = document.getElementById('mainpage').getAttribute('index');

GuiState.setProject(navengagement, navproject)
window.onload = add_links();
