//Exceptions

import { Util } from './util.js';

var Exceptions = {
    addexceptions : function(response) {
        var datapage = document.getElementById('datapage');
        var prdata = document.getElementById('prdata');

        var new_exception_data = this.get_exceptions_data(response);

        datapage.replaceChild(new_exception_data, prdata);
    },

    get_exceptions_data : function(response) {
        var new_exception_data = document.createElement('div');
        new_exception_data.setAttribute('id', 'prdata');

        var table = document.createElement('table');
        table.setAttribute('id', 'datatable');

        var header_row = document.createElement('tr');
        Util.add_table_header('Method', header_row);
        Util.add_table_header('Start-pc', header_row);
        Util.add_table_header('End-pc', header_row);
        Util.add_table_header('Handler-pc', header_row);
        Util.add_table_header('Handler', header_row);
        table.appendChild(header_row);
    
        for (var cmsix in response) {
            var exceptions = response[cmsix];
        
            for(var i = 0; i < exceptions.length; i++){
                var drow = document.createElement('tr');
                var exception_handler = exceptions[i];  
            
                if(i == 0) {
                    var methodname = exception_handler[4] + " ( " + cmsix + " )"; 
                
                    var dname = Util.add_table_data_with_link(methodname, drow, Util.get_method_link(cmsix));
                    dname.rowSpan = exceptions.length;
                    //MethodBytecode.link_to_method_bytecode(dname, cmsix);
                }   
            
                var dstartpc = document.createElement('td');
                var dendpc = document.createElement('td');
                var dhandlerpc = document.createElement('td');
                var dsource = document.createElement('td');
            
                Util.append_text_to_node(dstartpc, exception_handler[0]);
                Util.append_text_to_node(dendpc, exception_handler[1]);
                Util.append_text_to_node(dhandlerpc, exception_handler[2]);
                Util.append_text_to_node(dsource, exception_handler[3]);
            
                dstartpc.setAttribute('class', 'rightalign');
                dendpc.setAttribute('class', 'rightalign');
                dhandlerpc.setAttribute('class', 'rightalign');
            
                drow.appendChild(dstartpc);
                drow.appendChild(dendpc);
                drow.appendChild(dhandlerpc);
                drow.appendChild(dsource);
            
                table.appendChild(drow);
            }   
        }   
    
        new_exception_data.appendChild(table);
    
        return new_exception_data;
    }   
}

export { Exceptions };
