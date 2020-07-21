//Classes

import { Util } from './util.js';
import { GuiState } from './guistate.js';
import { Bytecode } from './bytecode.js';

var Classes = {
    addproject : function(response, navengagement, navproject) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_class_data = this.get_class_data(response, navengagement, navproject);

        datapage.replaceChild(new_class_data, prdata);
    },

    // TODO : Refine method arguments
    get_class_data : function(response, navengagement, navproject) {
        var classnames = response;

        var new_class_data = document.createElement('div');
        new_class_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id','datatable');
        table.classList.add('classtable');
        table.classList.add('balanced');

        var header_row = document.createElement('tr');
        Util.add_table_header('Classes', header_row);
        table.appendChild(header_row);

        for (var classname in classnames) {
            var cnix = classnames[classname];

            var drow = document.createElement('tr');
            //var dname = document.createElement('td');
			var txt = classname + " ( " + cnix + " ) ";
			var linktxt = "/bytecode/" + GuiState.engagement + "/" + GuiState.project + "/" + cnix;

			Util.add_table_data_with_link(txt, drow, linktxt);

            //drow.style.border = '0px';
            //dname.style.border = '0px';

            //Util.append_text_to_node(dname, classname + " ( " + cnix + " ) ");

			//var link = document.createElement('a');
            //link.setAttribute('href', "/loadbytecode/" + navengagement + "/" + navproject);
            //link.setAttribute('target', '_blank');

            //var callee = "loadbytecode(" + '"' + navengagement + '","' + navproject + '","' + cnix + '"' + ")";
            //var callee = "loadbytecode(" + '"' + currentState.engagement + '","' + currentState.project + '","' + cnix + '"' + ")";

            //dname.addEventListener("click", function(navengagment, navproject) {
            //    loadbytecode(navengagement, navproject)
            //});
            //dname.setAttribute("onclick",callee);
            //dname.setAttribute("class", "clickable");

            //drow.appendChild(dname)
            table.appendChild(drow);
        }

        new_class_data.appendChild(table);

        return new_class_data;
    }
}

export { Classes };
