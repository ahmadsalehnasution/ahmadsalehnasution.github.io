$('.item').on('click','li', function(){
   $(this).children(".subitem").show().end().siblings().find('.subitem').hide();
});
