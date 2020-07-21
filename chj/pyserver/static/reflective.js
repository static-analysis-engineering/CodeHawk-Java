//Reflective Calls

import { Util } from './util.js';
import { MethodBytecode } from './methodbytecode.js';

var Reflective = {
    addreflective : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_reflective_data = this.get_reflective_data(response);

        datapage.replaceChild(new_reflective_data, prdata);
    },

    get_reflective_data : function(response) {
        var reflectivemethods = response;

        var new_reflective_data = document.createElement('div');
        new_reflective_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');
        table.classList.add('balanced');

        var header_row = document.createElement('tr');
        Util.add_table_header('Method', header_row);
        Util.add_table_header('PC', header_row);
        Util.add_table_header('Call', header_row);
        table.appendChild(header_row);

        for (var cmsix in reflectivemethods) {
            var methodcalls = response[cmsix]['pcs'];
            var methodname = response[cmsix]['name'] + ' ( ' + cmsix + ' )';

            for (var call in methodcalls) {
                var drow = document.createElement('tr');

                //var dname = document.createElement('td');
                var dpc = document.createElement('td');
                var dcall = document.createElement('td');

                //Util.append_text_to_node(dname, methodname);
                Util.append_text_to_node(dpc, call);
                Util.append_text_to_node(dcall, methodcalls[call]);

                //MethodBytecode.link_to_method_bytecode( dname, cmsix ); 

                dpc.setAttribute('class', 'rightalign');

                Util.add_table_data_with_link(methodname, drow, MethodBytecode.get_link(cmsix));
                //drow.appendChild(dname);
                drow.appendChild(dpc);
                drow.appendChild(dcall)

                table.appendChild(drow);
            }
        }
        new_reflective_data.appendChild(table);

    return new_reflective_data;
    }
}

export { Reflective };
