//Branches

"use strict";

import { Util } from './util.js';
import { GuiState } from './guistate.js';

var MethodBytecode = {
	loadmethodbytecode : function(engagement, project, cmsix) {
    	//var restoringCall = "loadmethodbytecode('" + engagement + "','" + project + "','" + cmsix + "')";
    	//save_history(restoringCall, "methodbytecode");

        var url = "/methodbytecode/" + engagement + "/" + project + "/" + cmsix;
        var request = new XMLHttpRequest();
        request.onload = function() {
            if (request.status == 200) {
                var response = JSON.parse(request.responseText);
                if (response['meta']['status'] == 'ok') {
                    MethodBytecode.addmethodbytecode(response['content']);
                } else {
                    alert('Server Error');
                }
            }
        };
        request.open("GET", url);
        request.send();
    },

    get_link : function(cmsix) {
        return "/methodbytecode/" + GuiState.engagement + "/" + GuiState.project + "/" + cmsix;
    },

    addmethodbytecode : function(response) {
        var datapage = document.getElementById('datapage');
        var data = document.getElementById('data');

        var new_bytecode_data = this.get_method_bytecode_data(response);

        datapage.replaceChild(new_bytecode_data, data);
    },

    get_method_bytecode_data : function(response) {
        var bytecodes = response;

        var new_bytecode_data = document.createElement('div');
        new_bytecode_data.setAttribute('id', 'data');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');
        table.classList.add('balanced');

        var header_row = document.createElement('tr');
        Util.add_table_header('PC', header_row);
        Util.add_table_header('Instruction', header_row);
        table.appendChild(header_row);

        for (var i = 0; i < bytecodes.length; i++) {
            var bytecode = bytecodes[i];

            var drow = document.createElement('tr');

            Util.add_table_borderless(bytecode[0], drow);
            Util.add_table_borderless(bytecode[1], drow);

            table.appendChild(drow);
        }

        new_bytecode_data.appendChild(table);

        return new_bytecode_data;
	},

    link_to_method_bytecode: function(dname, cmsix) {
	    dname.setAttribute('cmsix', cmsix);
	    dname.addEventListener('click', function() {
		    var cmsix = this.getAttribute('cmsix');
		    MethodBytecode.loadmethodbytecode(GuiState.engagement, GuiState.project, cmsix)}
		    );
	    dname.setAttribute("class", "clickable");
    }
}

export { MethodBytecode };
