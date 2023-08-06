$(function($){

    var includes = $("div#collage.edit div.collage-header a.post, div#collage.edit div.collage-header span.row-create, div#collage.edit div.collage-header a.action");
    var excludes = $("div#collage.edit div.collage-header a.layout");
    
    var trans = {
        "split"  : 'diviser',
        "create" : 'créer',
    };

    
    $.each(includes, function(i, obj){
        
        if ($.inArray(obj, excludes) == -1) {
            
            if (obj.tagName == "SPAN") {
                obj = $(obj).parent("a");
            }
            var txt = $(obj).text().trim().toLowerCase();
            $(obj).text( (trans[txt] ? trans[txt] : txt ) );
            $(obj).removeClass();
            $(obj).toggleClass("bouton-collage");
            $(obj).toggleClass("bouton-collage-"+txt);
        }
        
    });
    
    /*********************************************************************/
    
    $.each($("img[alt=CollageRow]"), function(i, obj){
        $(obj).attr("src", "++resource++jalonedit.theme.images/collagerow_icon.png");
    });
    
    $.each($("img[alt=CollageColumn]"), function(i, obj){
        $(obj).attr("src", "++resource++jalonedit.theme.images/collagecolumn_icon.png");
    });  
        
    /*********************************************************************/
    
    $('.collage-header').animate({opacity: 1}, 2000);
    
    /*********************************************************************/
    
    
    $.each($("#insert-collage-row"), function(i, obj){
        $(obj).val("Ajouter une ligne");
    });
    
    //var pref = "";//"div#collage.edit";
    trans = [
        ["span.discreet"        , "Empty composition. Add one or more rows to get started." , "La composition est vide. Ajouter une ligne pour commencer."],
        ["dl.portalMessage dd"  , "Row was added."                                          , "La ligne a été ajoutée"],
    
    ]; 
    //console.log(trans);
    
    
    $.each(trans, function(i, obj){
        $(obj[0]+":contains("+obj[1]+")").text(obj[2]);
    });
    
    
});