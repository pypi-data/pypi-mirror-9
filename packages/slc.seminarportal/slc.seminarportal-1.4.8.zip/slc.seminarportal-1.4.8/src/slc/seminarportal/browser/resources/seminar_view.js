jQuery(document).ready(function(){
    "use strict";

    jQuery("div.big-target a").bigTarget({
        clickZone : 'div:eq(0)' // jQuery parent selector
    });
});
