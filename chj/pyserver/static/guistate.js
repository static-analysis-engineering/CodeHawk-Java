//State

var GuiState = {
    setState : function(navselected, engagement, project) {
        this.navselected = navselected;
        this.engagement = engagement;
        this.project = project;
    },

    setNav : function(navselected) {
        this.navselected = navselected;
    },

    setProject : function(engagement, project) {
        this.engagement = engagement;
        this.project = project;
    }
}

//var History = {
//    historyEntry : function(restoringCall, title) {
//        this.restoringCall = restoringCall;
//        this.title = title;
//        this.navselected = 
//    }
//}

export { GuiState };
