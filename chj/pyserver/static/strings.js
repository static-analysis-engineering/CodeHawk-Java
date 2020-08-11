//Strings

import { Util } from './util.js';

var Strings = {
    addstrings : function(response) { 
        var datapage = document.getElementById('datapage'); 
        var prdata = document.getElementById('prdata');    
 
        var new_string_data = this.get_strings_data(response); 
 
        datapage.replaceChild(new_string_data, prdata); 
    },

    get_strings_data : function(response) {
        var new_string_data = document.createElement('div');
        new_string_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');

        var header_row = document.createElement('tr');
        Util.add_table_header('Method', header_row);
        Util.add_table_header('pc', header_row);
        Util.add_table_header('String', header_row);
        table.appendChild(header_row);

        for (var cmsix in response) {
            var methodname = response[cmsix]['name'] + " ( " + cmsix + " )";
            var pcs = response[cmsix]['pcs'];

            var count = 0;
            for (var pc in pcs) {
                var drow = document.createElement('tr');

                if (count == 0) {
                    var dname = document.createElement('td');
                    var dname_text = document.createTextNode(methodname);
                    dname.appendChild(dname_text);

                    var dname = Util.add_table_data_with_link(methodname, drow, Util.get_method_link(cmsix));
                    dname.rowSpan = Object.keys(pcs).length;
                
                    //MethodBytecode.link_to_method_bytecode(dname, cmsix);

                    //drow.appendChild(dname);
                }
                count += 1;

                var dpc = document.createElement('td');
                var dstring = document.createElement('td');

                Util.append_text_to_node(dpc, pc);
                Util.append_text_to_node(dstring, pcs[pc]);

                dpc.setAttribute('class', 'rightalign');
                dstring.setAttribute('class', 'breakable');

                drow.appendChild(dpc);
                drow.appendChild(dstring);

                table.appendChild(drow);
            }
        }

        new_string_data.appendChild(table);

        return new_string_data;
    }
}

export { Strings };
