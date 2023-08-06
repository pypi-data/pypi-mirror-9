var common_content_filter = '#content>*';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};
var common_close_filter = 'input[name=form.button.cancel]';

jQuery.extend(jQuery.tools.overlay.conf, common_jqt_config);

jQuery(function($){
    $('a.showmore').prepOverlay({
        subtype:"ajax",
        filter:common_content_filter,
        closeselector:common_close_filter,
        formselector: 'form#glossaire-base-edit, form#link-base-edit, form#bibliographie-base-edit',
        noform: 'close',
        config:{
        	closeOnClick:false,
            onLoad:function() {
                loadTinMCE()
            }
        }
    });
});

function loadTinMCE(){
      $('textarea.mce_editable').each(function() {
        var config = new TinyMCEConfig($(this).attr('id'));
        config.init();
      });
}