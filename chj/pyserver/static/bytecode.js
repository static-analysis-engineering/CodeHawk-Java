//Class Bytecode

import { Util } from './util.js';
import { GuiState } from './guistate.js';

var Bytecode = {
    addbytecode : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_bytecode_data = this.get_bytecode_data(response);

        datapage.replaceChild(new_bytecode_data, prdata);
    },

    loadbytecode : function(engagement, project, cnix) {
        //var restoringCall = "loadbytecode('" + engagement + "','" + project + "','" + cnix + "')";
        //save_history(restoringCall, "bytecode");

        var url = "/bytecode/" + engagement + "/" + project + "/" + cnix;
        var request = new XMLHttpRequest();
        request.onload = function() {
            if (request.status == 200) {
                var response = JSON.parse(request.responseText);
                if (response['meta']['status'] == 'ok') {
                    Bytecode.addbytecode(response['content']);
                }
            } else {
                alert('Server Error');
            }
        };
        request.open("GET", url);
        request.send()
    },

    get_bytecode_data : function(response) {
        var methods = response;

        var new_bytecode_data = document.createElement('div');
        new_bytecode_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');

        var header_row = document.createElement('tr');
        Util.add_table_header('PC', header_row);
        Util.add_table_header('Instruction', header_row);
        table.appendChild(header_row);

        for(var method in methods) {
            var bytecodes = methods[method];

            var drow = document.createElement('tr');
            var dname = document.createElement('td');

            Util.append_text_to_node(dname, method);
            dname.colSpan = 2;

            /*var linktxt = "/methodbytecode/" + GuiState.engagement + "/" + GuiStateproject + "/" + cmsix;
            dname = Util.add_table_data_with_link(method, drow, linktxt);
            dname.colSpan = 2;*/

            drow.appendChild(dname);
            table.appendChild(drow);

            for (var i = 0; i < bytecodes.length; i++) {
                var bytecode = bytecodes[i];

                var drow = document.createElement('tr');

                Util.add_table_borderless(bytecode[0], drow);
                Util.add_table_borderless(bytecode[1], drow);

                table.appendChild(drow);
            }
        }

        new_bytecode_data.appendChild(table);

        return new_bytecode_data;
    }
}

export { Bytecode };
