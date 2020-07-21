//Branches

import { Util } from './util.js';
import { MethodBytecode } from './methodbytecode.js';

var Branches = {
    addbranches : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_branch_data = this.get_branch_data(response);

        datapage.replaceChild(new_branch_data, prdata);
    },

    get_branch_data : function(response) {
        var branches = response

        var new_branch_data = document.createElement('div');
        new_branch_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id','datatable');

        var header_row = document.createElement('tr');
        Util.add_table_header('Branch Condition', header_row);
        Util.add_table_header('Method', header_row);
        table.appendChild(header_row);

        for (var condition in branches) {

            var locations = branches[condition];

            var dcondition = document.createElement('td');
            dcondition.rowSpan = locations.length;
            Util.append_text_to_node(dcondition, condition);
            dcondition.setAttribute('class', 'breakable');

            for ( var i = 0 ; i < locations.length ; i++ ) {
                var drow = document.createElement('tr');

                //var dinfo = document.createElement('td');
                var cmsix = locations[i][0];
                var methodinfo = locations[i][1] + " ( " + cmsix + " )";
                //Util.append_text_to_node(dinfo, methodinfo);

                //MethodBytecode.link_to_method_bytecode(dinfo, cmsix);

                if (i == 0) { drow.appendChild(dcondition); }
                var dinfo = Util.add_table_data_with_link(methodinfo, drow, MethodBytecode.get_link(cmsix));
				dinfo.setAttribute('cmsix', cmsix);
                
                //drow.appendChild(dinfo);

                table.appendChild(drow);
            }
        }

        new_branch_data.appendChild(table);

        return new_branch_data;
    }
}

export { Branches };
