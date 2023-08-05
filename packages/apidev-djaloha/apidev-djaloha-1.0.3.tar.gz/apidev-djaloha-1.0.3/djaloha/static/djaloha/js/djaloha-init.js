(function (window, undefined) {
    var Aloha = window.Aloha;
    
    Aloha.ready( function() {
        // Make #content editable once Aloha is loaded and ready.
        Aloha.jQuery('.djaloha-editable').aloha();
        
        Aloha.jQuery("body").bind('aloha-image-resized', function(event, img){
            //Callback called when the fragment edition is done -> Push to the page
            $(img).attr('width', $(img).width());
            $(img).attr('height', $(img).height());
        });
        
    });

    Aloha.bind('aloha-editable-deactivated', function(event, eventProperties){
        //Callback called when the fragment edition is done -> Push to the page
        var ed = eventProperties.editable;
        
        var html = $('#'+eventProperties.editable.getId()).html();
        $("#"+ed.getId()+"_hidden").val($.trim(html));
        
        //$("#"+ed.getId()+"_hidden").val($.trim(ed.getContents()));
    });

})(window);
