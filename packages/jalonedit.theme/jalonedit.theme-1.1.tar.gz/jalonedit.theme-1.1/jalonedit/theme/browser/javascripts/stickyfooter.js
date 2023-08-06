$(window).bind("load", function() { 
       function positionFooter() {
       
            $.each($("#footer"), function(i, obj){
                
                var footerHeight = $(obj).height();
                var footerTop = ($(window).scrollTop()+$(window).height()-footerHeight);

               if ( ($(document.body).height()+footerHeight) < $(window).height()) {
                   $(obj).css({
                        position: "absolute",
                        top: footerTop+"px",
                   })
                   
                   $.each($("#portal-column-one, #portal-column-two"), function(i, o) { 
                        var top = $(o).offset().top;
                        $(o).css({height:footerTop-top});
                    });
                   
               } else {
                   $(obj).css({
                        position: "static"
                   })
               }
               
             });

       }

       positionFooter();
       $(window).scroll(positionFooter).resize(positionFooter);

});