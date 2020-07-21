//Loops

import { Util } from './util.js';
import { MethodBytecode } from './methodbytecode.js';
import { GuiState } from './guistate.js';

var Loops = {
    addloops : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_loop_data = this.get_loop_data(response);

        datapage.replaceChild(new_loop_data, prdata);
    },

    get_loop_data : function(response) {
        var loops = response;

        var new_loop_data = document.createElement('div');
        new_loop_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');
        table.classList.add('balanced');

        var header_row = document.createElement('tr');
        Util.add_table_header_with_sort('#Loops', header_row, 'datatable', 0, Util.compareInt, Util.compareInt, true);
        Util.add_table_header_with_sort('Max Depth', header_row, 'datatable', 1, Util.compareInt, Util.compareInt, true);
        Util.add_table_header('Bounds', header_row);
        Util.add_table_header('Taints', header_row);
        Util.add_table_header('Method Name (id)', header_row);
        table.appendChild(header_row);

        for (var cmsix in loops) {
            var sample = loops[cmsix];

            var drow = document.createElement('tr');

            var dloopcount = document.createElement('td');
            var dmaxdepth = document.createElement('td');
            var dloopbounds = document.createElement('td');
            var dlooptaints = document.createElement('td');

            dloopcount.textContent = sample["loopcount"];
            dmaxdepth.textContent = sample["max-depth"];
            dloopbounds.textContent = sample["loopbounds"];
            dlooptaints.textContent = sample["looptaints"];

            //MethodBytecode.link_to_method_bytecode(dname, cmsix);

            dloopcount.setAttribute('class', 'rightalign');
            dmaxdepth.setAttribute('class', 'rightalign');

            drow.appendChild(dloopcount);
            drow.appendChild(dmaxdepth);
            drow.appendChild(dloopbounds);
            drow.appendChild(dlooptaints);

            var methodname = sample["aqname"] + " (" + cmsix + ")";
            var linktxt = "/methodbytecode/" + GuiState.engagement + "/" + GuiState.project + "/" + cmsix;
            Util.add_table_data_with_link(methodname ,drow, linktxt);

            table.appendChild(drow);
        }

        new_loop_data.appendChild(table);

        return new_loop_data;
    }
}

export { Loops };
