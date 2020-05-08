/* ==================================================================
 * Globals
 * ------------------------------------------------------------------
*/

"use strict";

import { Util } from './util.js';
import { Branches } from './branches.js';
import { Classes } from './classes.js';
import { Costs } from './costs.js';
import { Exceptions } from './exceptions.js';
import { Loops } from './loops.js';
import { Recursive } from './recursive.js';
import { Reflective } from './reflective.js';
import { SFInits } from './staticfieldinits.js';
import { Strings } from './strings.js';
import { TaintOrigins } from './taintorigins.js';

import { GuiState } from './guistate.js';

var projects = null;

//var historylock = false;

/* ==================================================================
 * XmlHttpRequest functions
 * ------------------------------------------------------------------
*/

//function HistoryEntry(restoringCall, title) {
//    this.restoringCall = restoringCall;
//    this.title = title;
//    this.navselected = currentState.navselected;
//    this.engagement = currentState.engagement;
//    this.project = currentState.project;
//}

function loadprojects() {
    var url = "/loadprojects";
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            addprojectlist(response['content']);
        }
        else {
            alert('Projects could not be loaded: ' + response['meta']['reason']);
        }
    } else {
        alert('Server error');
    }
    };
    request.open("GET", url);
    request.send();
}

function loadbranches(engagement, project) {
    //var restoringCall = "select_nav('navbr')"
    //save_history(restoringCall, "branches");

    var url = "/branches/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
        var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
                Branches.addbranches(response['content']);
            }
        } else {
            alert('Server Error');
        }
    }; 
	request.open("GET",url);
    request.send();
}

function loadcosts(engagement, project) {
    //var restoringCall = "select_nav('navco')"
    //save_history(restoringCall, "costs");

    var url = "/costs/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
                var count = 0;
                for (var x in response['content']) {
                    for (var y in response['content'][x]) {
                        count += 1;
                    }
                }
                if (count > 0) {
                    Costs.addcosts(response['content']);
                } else {
                    alert('Cost data not found! You may need to generate it first.');
                }
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadexceptions(engagement, project) {
    //var restoringCall = "select_nav('navex')"
    //save_history(restoringCall, "exceptions");

    var url = "/exceptions/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
               Exceptions.addexceptions(response['content']);
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadproject(engagement, project) {
    //var restoringCall = "select_nav('navpr')"
    //save_history(restoringCall, "classes");
    
    var url = "/project/" + engagement  + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            Classes.addproject(response['content'], GuiState.engagement, GuiState.project);
        }
    } 
    else {
        alert('Server error');
    }
    };
    request.open("GET",url);
    request.send();
}

function loadloops(engagement, project) {
    //var restoringCall = "select_nav('navlo')"
    //save_history(restoringCall, "loops");

    var url = "/loops/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
    if (request.status == 200) {
        var response = JSON.parse(request.responseText);
        if (response['meta']['status'] == 'ok') {
            Loops.addloops(response['content']);
        } 
    } else {
        alert('Server error');
    }
    };
    request.open("GET",url);
    request.send();
}

function loadstrings(engagement, project) {
    //var restoringCall = "select_nav('navst')"
    //save_history(restoringCall, "strings");

    var url = "/strings/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
               Strings.addstrings(response['content']);
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadrecursive(engagement, project) {
    //var restoringCall = "select_nav('navrec')"
    //save_history(restoringCall, "recursives");

    var url = "/recursive/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
               Recursive.addrecursive(response['content']);
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadreflective(engagement, project) {
    //var restoringCall = "select_nav('navref')"
    //save_history(restoringCall, "reflective");

    var url = "/reflective/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
               Reflective.addreflective(response['content']);
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadstaticfieldinits(engagement, project) {
    //var restoringCall = "select_nav('navsfinit')"
    //save_history(restoringCall, "static field initializers");

    var url = "/staticfieldinits/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
               SFInits.addstaticfieldinits(response['content']);
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function loadtaintorigins(engagement, project) {
    //var restoringCall = "select_nav('navta')"
    //save_history(restoringCall, "taint origins");

    var url = "/taintorigins/" + engagement + "/" + project;
    var request = new XMLHttpRequest();
    request.onload = function() {
        if (request.status == 200) {
            var response = JSON.parse(request.responseText);
            if (response['meta']['status'] == 'ok') {
                var count = 0;
                for (var x in response['content']) {
                    count += 1;
                }
                if (count > 0) {
                    TaintOrigins.addtaintorigins(response['content']);
                } else {
                    alert('Taint data not found! You may need to generate it first.');
                }
            }
        } else {
            alert('Server Error');
        }
    };
    request.open("GET", url);
    request.send()
}

function select_project(engagement, name) {
    if (GuiState.engagement && GuiState.project) {
        document.getElementById(GuiState.engagement + GuiState.project).removeAttribute('class');
    }

    var next = document.getElementById(engagement + name);
    next.setAttribute('class','xselected');

	GuiState.setProject(engagement, name);
    if (GuiState.navselected == 'navlo') { 
        loadloops(engagement, name);
    }
    else if (GuiState.navselected == 'navpr') {
        loadproject(engagement, name);
    }
    else if (GuiState.navselected == 'navbr') {
        loadbranches(engagement, name);
    }
    else if(GuiState.navselected == 'navco') {
        loadcosts(engagement, name);
    }
    else if(GuiState.navselected == 'navex') {
        loadexceptions(engagement, name);
    }
    else if(GuiState.navselected == 'navst') {
        loadstrings(engagement, name);
    }
    else if(GuiState.navselected == 'navrec') {
        loadrecursive(engagement, name);
    }
    else if(GuiState.navselected == 'navref') {
        loadreflective(engagement, name);
    }
    else if(GuiState.navselected == 'navsfinit') {
        loadstaticfieldinits(engagement, name);
    }
    else if(GuiState.navselected == 'navta') {
        loadtaintorigins(engagement, name);
    }
}

function select_nav(navitem) {
    if (GuiState.navselected) {
        document.getElementById(GuiState.navselected).removeAttribute('class');
    }

    var next = document.getElementById(navitem);
    next.setAttribute('class', 'selected');

    GuiState.navselected = navitem;

    if (projects == null) {
        loadprojects();
    } else {
        if (GuiState.engagement && GuiState.project) {
            select_project(GuiState.engagement, GuiState.project);
        } else {
            alert('Please select a project first');
        }
    }
}

/* ==================================================================
 * Functions that manipulate the DOM
 * ------------------------------------------------------------------
*/

function addprojectlist(response) {
    projects = response;
    var el = document.getElementById('sidebar');
    var contents = document.getElementById('projects');

    var newcontents = document.createElement('ul');
    newcontents.setAttribute('id', 'projects');

    for (var p in response) {
        var listitem = document.createElement('li');
        var spanitem = document.createElement('span');
        spanitem.setAttribute('class','caret');
        spanitem.textContent = p;
        listitem.appendChild(spanitem);
        newcontents.appendChild(listitem);
        var nestedlist = document.createElement('ul')
        nestedlist.setAttribute('class','nested');
        nestedlist.setAttribute('id','xlist');
        listitem.appendChild(nestedlist);

        var engagementname = p;
        for (var i = 0; i < response[p].length; i++) {
            var projectname = response[p][i];

            var xlistitem = document.createElement('li');
            var xspanitem = document.createElement('span');
            xlistitem.addEventListener('click', function() {
                var xengagement = this.getAttribute('eng');
                var xproject = this.getAttribute('exe');
                select_project(xengagement, xproject);
            })
            xlistitem.setAttribute('eng', engagementname);
            xlistitem.setAttribute('exe', projectname);
            xlistitem.id = engagementname + projectname;
            xspanitem.innerText = projectname;
            xlistitem.appendChild(xspanitem);
            nestedlist.appendChild(xlistitem);

        }
    }

    el.replaceChild(newcontents,contents);

    var toggler = document.getElementsByClassName("caret");

    for(var i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener("click", function() {
        this.parentElement.querySelector(".nested").classList.toggle("active");
        this.classList.toggle("caret-down");
    } );
    }
}

//function link_to_method_bytecode(dname, cmsix) {
//    var callee = "loadmethodbytecode(" + '"' + GuiState.engagement + '","' + GuiState.project + '","' + cmsix + '"' + ")";
//    dname.setAttribute("onclick", callee);
//    dname.setAttribute("class", "clickable");
//}

//function save_history(restoringCall, title) {
//    if(historylock == false) {
//        var historyEntry = new HistoryEntry(restoringCall, title, currentState.navselected, currentState.engagement, currentState.project, currentState.index);
//        history.pushState(JSON.stringify(historyEntry), currentState.pagetype);
//    }
//}

//window.onpopstate = function(event) {
//    var historyEntry = JSON.parse(event.state);

//    document.getElementById(currentState.engagement + currentState.project).removeAttribute('class');
//    currentState.engagement = historyEntry.engagement;
//    currentState.project = historyEntry.project;
//    document.getElementById(currentState.engagement + currentState.project).setAttribute('class','xselected');

//    document.getElementById(currentState.navselected).removeAttribute('class');
//    currentState.navselected = historyEntry.navselected;
//    document.getElementById(currentState.navselected).setAttribute('class', 'selected');

//    console.log(historyEntry.restoringCall);
//    historylock = true;
//    eval(historyEntry.restoringCall);
//    historylock = false;
//}

function add_nav_listener(tag) {
    document.getElementById(tag).addEventListener('click', function() {select_nav(tag)})
}

add_nav_listener('navpr');
add_nav_listener('navlo');
add_nav_listener('navbr');
add_nav_listener('navco');
add_nav_listener('navst');
add_nav_listener('navex');
add_nav_listener('navrec');
add_nav_listener('navref');
add_nav_listener('navsfinit');
add_nav_listener('navta');

GuiState.setState('navpr', null, null)
window.onload = loadprojects()
