//Recursive Methods

import { Util } from './util.js';

var Recursive = {
    addrecursive : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_recursion_data = this.get_recursive_data(response);

        datapage.replaceChild(new_recursion_data, prdata);
    },

    get_recursive_data : function(response) {
        var recursivecalls = response;

        var new_recursion_data = document.createElement('div');
        new_recursion_data.setAttribute('id', 'prdata')

        var recursivecalls = response["recursivecalls"];
        if (recursivecalls.length > 0) {
            var table1 = document.createElement('table');
            table1.setAttribute('id', 'datatable');
            table1.classList.add('balanced')
            var header_row = document.createElement('tr');
            Util.add_table_header("Self-Recursive Methods", header_row);
            table1.appendChild(header_row);

            for (var i = 0; i < recursivecalls.length; i++) {
                var drow = document.createElement('tr');

                var cmsix = recursivecalls[i][0];
                var methodname = Util.build_method_name(recursivecalls[i][1], cmsix);
                Util.add_table_data_with_link(methodname, drow, Util.get_method_link(cmsix));

                table1.appendChild(drow);
            }
            new_recursion_data.appendChild(table1);
        }

        var mutualrecursivecalls = response["mutualrecursivecalls"];
        if (mutualrecursivecalls.length > 0) {
            var table2 = document.createElement('table');
            table2.setAttribute('id', 'datatable');
            table2.classList.add('balanced');
            var header_row = document.createElement('tr');
            Util.add_span_table_header("Mutually Recursive Methods", header_row, 2);
            table2.appendChild(header_row);

            for (var i = 0; i < mutualrecursivecalls.length; i++) {
                var drow = document.createElement('tr');

                var callercmsix = mutualrecursivecalls[i][0];
                var calleecmsix = mutualrecursivecalls[i][2];
                var callername = Util.build_method_name(mutualrecursivecalls[i][1], callercmsix);
                var calleename = Util.build_method_name(mutualrecursivecalls[i][3], calleecmsix);
                Util.add_table_data_with_link(callername, drow, Util.get_method_link(callercmsix));
                Util.add_table_data_with_link(calleename, drow, Util.get_method_link(calleecmsix));

                table2.appendChild(drow);
            }
            new_recursion_data.appendChild(table2);
        }

        var recursive2cycles = response["recursive2cycles"];
        if (recursive2cycles.length > 0) {
            var table3 = document.createElement('table');
            table3.setAttribute('id', 'datatable');
            table3.classList.add('balanced');
            var header_row = document.createElement('tr');
            Util.add_span_table_header("Size 2 cycles", header_row, 3);
            table3.appendChild(header_row);

            for (var i = 0; i < recursive2cycles.length; i++) {
                var drow1 = document.createElement('tr');
                var drow2 = document.createElement('tr');
                var drow3 = document.createElement('tr');

                var callercmsix = recursive2cycles[i][0]
                var calleecmsix = recursive2cycles[i][2]
                var subcalleecmsix = recursive2cycles[i][4]

                var callername = Util.build_method_name(recursive2cycles[i][1], callercmsix);
                var calleename = Util.build_method_name(recursive2cycles[i][3], calleecmsix);
                var subcalleename = Util.build_method_name(recursive2cycles[i][5], subcalleecmsix);

                var dcaller = Util.add_table_data_with_link(callername, drow1, Util.get_method_link(callercmsix));
                var dcallee = Util.add_table_data_with_link("==> " + calleename, drow2, Util.get_method_link(calleecmsix));
                var dsubcallee = Util.add_table_data_with_link("====> " + subcalleename, drow3, Util.get_method_link(subcalleecmsix));

                dcaller.style.border = '1px black';
                dcallee.style.border = '1px black';
                dsubcallee.style.border = '1px black';

                dcaller.style.borderStyle = 'solid solid hidden solid';
                dcallee.style.borderStyle = 'hidden solid hidden solid';
                dsubcallee.style.borderStyle = 'hidden solid solid solid';

                table3.appendChild(drow1);
                table3.appendChild(drow2);
                table3.appendChild(drow3);
            }
            new_recursion_data.appendChild(table3);
        }
        return new_recursion_data;
    }
}

export { Recursive };
