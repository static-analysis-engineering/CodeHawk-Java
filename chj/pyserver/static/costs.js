//Costs

import { Util } from './util.js';

var Costs = {
    addcosts : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_costs_data = this.get_costs_data(response);

        datapage.replaceChild(new_costs_data, prdata);
    },

    get_costs_data : function(response) {
        var costs = response;

        var new_costs_data = document.createElement('div');
        new_costs_data.setAttribute('id', 'prdata');

        var topcosts = costs['topcosts'];
        if (Object.keys(topcosts).length > 0) {
            var table1 = document.createElement('table');
            table1.setAttribute('id', 'datatable');
            table1.classList.add('balanced');
            var header_row = document.createElement('tr');
            Util.add_table_header('Cost', header_row);
            Util.add_table_header('Method', header_row);
            table1.appendChild(header_row);

            for (var cmsix in topcosts) {
                var drow = document.createElement('tr');
                var dcost = document.createElement('td');

                var cost = topcosts[cmsix]
                Util.append_text_to_node(dcost, cost[1]);
                dcost.setAttribute('class', 'rightalign');

                drow.appendChild(dcost);
                Util.add_table_data_with_link(cost[0], drow, Util.get_method_link(cmsix));

                table1.appendChild(drow);
            }
            new_costs_data.appendChild(table1);
        }

        var constantcosts = costs['constantcosts'];
        if (Object.keys(constantcosts).length > 0) {
            var table2 = document.createElement('table');
            table2.setAttribute('id', 'datatable');
            table2.classList.add('balanced');
            var header_row = document.createElement('tr');
            Util.add_table_header('Cost', header_row);
            Util.add_table_header('Method', header_row);
            table2.appendChild(header_row);

            for (var cmsix in constantcosts) {
                var drow = document.createElement('tr');
                var dcost = document.createElement('td');

                var cost = constantcosts[cmsix];
                Util.append_text_to_node(dcost, cost[1]);
                dcost.setAttribute('class', 'rightalign');

                drow.appendChild(dcost);
                Util.add_table_data_with_link(cost[0], drow, Util.get_method_link(cmsix));

                table2.appendChild(drow);
            }
            new_costs_data.appendChild(table2);
        }

        var rangecosts = costs['rangecosts'];
        if (Object.keys(rangecosts).length > 0) {
            var table3 = document.createElement('table');
            table3.setAttribute('id', 'datatable');
            table3.classList.add('balanced');
            var header_row = document.createElement('tr');
            Util.add_table_header('lower-bound', header_row);
            Util.add_table_header('upper-bound', header_row);
            Util.add_table_header('Method', header_row)
            table3.appendChild(header_row);

            for (var cmsix in rangecosts) {
                var cost = rangecosts[cmsix];

                var drow = document.createElement('tr');
                var dlb = document.createElement('td');
                var dub = document.createElement('td');

                Util.append_text_to_node(dlb, cost[1]);
                Util.append_text_to_node(dub, cost[2]);

                dlb.setAttribute('class', 'rightalign');
                dub.setAttribute('class', 'rightalign');

                drow.appendChild(dlb);
                drow.appendChild(dub);
                Util.add_table_data_with_link(cost[0], drow, Util.get_method_link(cmsix));

                table3.appendChild(drow);
            }
            new_costs_data.appendChild(table3);
        }

        return new_costs_data;
    }
}

export { Costs };
