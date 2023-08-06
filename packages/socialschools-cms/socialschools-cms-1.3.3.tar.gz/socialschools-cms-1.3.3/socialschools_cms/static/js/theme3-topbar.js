$(document).ready(function() {
  $(document).on("scroll",function(){
      if($(document).scrollTop()>0){
          $(".logo-theme-3-expandable").removeClass("logo-expanded").addClass("logo-collapsed");
      } else{
          $(".logo-theme-3-expandable").removeClass("logo-collapsed").addClass("logo-expanded");
      }
  });
});
