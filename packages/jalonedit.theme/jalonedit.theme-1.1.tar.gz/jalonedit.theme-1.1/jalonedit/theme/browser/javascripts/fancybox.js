jQuery(document).ready(function() {


//On ajoute un lien sur les images pour les avoir en taille reelle
  $("div#content .standard-document img").each(function() {
    imageSrc = $(this).attr("src");
    imageAlt = $(this).attr("alt");
    if (imageSrc.indexOf("/@@images") >= 0)
		{imageSrc = imageSrc.split('/@@images')[0];}
	if (imageSrc.indexOf("/image_preview") >= 0)
		{imageSrc = imageSrc.split('/image_preview')[0];}
		
    $(this).replaceWith("<a class='fancybox_link' rel='fancy_group' title='"+imageAlt+"' href='"+imageSrc+"'>"+$(this).parent().html()+"</a>");
  });


});


jq(function() {

//  jq("a[href$=.jpg],a[href$=.png],a[href$=.gif]").fancybox(
  jq("a.fancybox_link").fancybox(
    {
      'hideOnContentClick': false,
      'transitionIn' : 'elastic',
      'transitionOut' : 'elastic',
      'speedIn'  : 600, 
      'speedOut' : 200, 
      'overlayShow' : true,
      'titlePosition'  : 'inside',
      'type'  : 'image',

    });
//    jq("a.internal-link").fancybox();
    //console.log("fancybox ajoutee");
});