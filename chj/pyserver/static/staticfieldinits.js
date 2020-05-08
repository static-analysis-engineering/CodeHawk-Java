// Static Field Initializers

import { Util } from './util.js';
import { MethodBytecode } from './methodbytecode.js';

var SFInits = {
    addstaticfieldinits : function(response) {
        var prdata = document.getElementById('prdata');
        var datatable = document.getElementById('datatable');

        prdata.replaceChild(this.get_staticfieldinits_data(response), datatable);
    },

    get_staticfieldinits_data : function(response) {
        var sfinits = response;

        var new_sfinit_data = document.createElement('div');
        new_sfinit_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');

        var header_row = document.createElement('tr');
        Util.add_table_header('pc', header_row);
        Util.add_table_header('cmsix', header_row);
        table.appendChild(header_row);

        var initdict = sfinits['initdict']
        var readerdict = sfinits['readerdict']

        for (var cnix in initdict) {
            var drow = document.createElement('tr');
            var dcnix = document.createElement('td');
            dcnix.textContent = cnix;
            drow.appendChild(dcnix);
            table.appendChild(drow);
            
            for (var fsix in initdict[cnix]) {
                var drow = document.createElement('tr');
                var dfs = document.createElement('td');
                dfs.textContent = fsix;
                drow.appendChild(dfs);
                table.appendChild(drow)
                
                var drow = document.createElement('tr');
                var dinitializers = document.createElement('td');
                dinitializers.textContent = 'initializers';
                drow.appendChild(dinitializers);
                table.appendChild(drow)

                for (var cmsix in initdict[cnix][fsix]) {
                    var drow = document.createElement('tr');
                    var dpc = document.createElement('td');
                    dpc.textContent = initdict[cnix][fsix][cmsix][0];
                    drow.appendChild(dpc);
                    var cms = initdict[cnix][fsix][cmsix][1];
                    Util.add_table_data_with_link_mouseover(cms, drow, MethodBytecode.get_link(cmsix));
                    table.appendChild(drow);
                }

                var drow = document.createElement('tr');
                var dinitializers = document.createElement('td');
                dinitializers.textContent = 'readers';
                drow.appendChild(dinitializers);
                table.appendChild(drow)

                if (cnix in readerdict && fsix in readerdict[cnix]) {
                    for(var cmsix in readerdict[cnix][fsix]) {
                        var drow = document.createElement('tr');
                        var dpc = document.createElement('td');
                        dpc.textContent = readerdict[cnix][fsix][cmsix][0];
                        drow.appendChild(dpc);
                        var cms = readerdict[cnix][fsix][cmsix][1];
                        Util.add_table_data_with_link_mouseover(cms, drow, MethodBytecode.get_link(cmsix));
                        table.appendChild(drow);
                    }
                }
            }
        }

        return table;
    }
}

export { SFInits };
