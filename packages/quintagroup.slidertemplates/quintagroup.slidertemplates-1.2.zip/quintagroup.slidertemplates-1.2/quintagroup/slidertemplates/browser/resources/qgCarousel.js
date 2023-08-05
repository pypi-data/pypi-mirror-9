$.fn.qgCarousel = function () {

  var base = $(this);

  $(".qg-carousel").css("display", "block");
  $(".qg-wrapper .qg-item:first-child").addClass("active");
  $("<div class=\"qg-buttons\"><div class=\"qg-prev\">prev</div><div class=\"qg-next\">next</div></div>").insertBefore(base.children(".qg-wrapper-outer"));
  
  function widthCalculate () {

    var widthWrapperOuter = base.width();
    var item = base.find(".qg-item");
    var itemActive = base.find(".qg-item.active");
    var itemBeforeActive = item.index(itemActive);

    item.css(removeTransition());
    item.find(".portletItem").css(removeTransition());
    itemActive.css(removeTransition());
    base.find('.qg-wrapper').css(removeTransition());
    item.find(".image_block").css(removeTransition());
    item.find(".documentDescription").css(removeTransition());
    if ($(window).width() >= 768) {

      var activeWidth = widthWrapperOuter * 0.5875;
      var itemWidth = widthWrapperOuter * 0.175;
      var imageWidth = widthWrapperOuter * 0.38125;
      var itemWidthDescktop = widthWrapperOuter/5;
      var wrapperWidthDescktop = activeWidth *(item.length+2);

      item.css({'width':itemWidth});
      item.find(".portletItem").css({'height':imageWidth})
      itemActive.css({'width':activeWidth});
      var pixels = -(itemBeforeActive*(itemWidth+30));
      item.parent().css({'width':wrapperWidthDescktop});
      item.parent().css(doTransform(pixels));
      item.find(".image_block").css({'width':itemWidth,'height':itemWidth});
      itemActive.find(".image_block").css({'width':imageWidth,'height':imageWidth});
      item.find(".documentDescription").css({'height':itemWidthDescktop/2-45});
      itemActive.find('.documentDescription').css({'height':itemWidthDescktop-4});
    } else if ($(window).width() >= 480) {
      var wrapperWidthPhone = widthWrapperOuter * item.length;
      item.css({'width':widthWrapperOuter});
      var pixels = -(itemBeforeActive*widthWrapperOuter);
      item.parent().css({'width':wrapperWidthPhone+100});
      item.parent().css(doTransform(pixels));
      item.find(".image_block").css({'width':widthWrapperOuter*2/3,'height':widthWrapperOuter*2/3});
      itemActive.find('.documentDescription').css({'height':widthWrapperOuter*1/3+10});
      item.find(".portletItem").css({'height':widthWrapperOuter*2/3})
    } else {
      var wrapperWidthPhone = widthWrapperOuter * item.length;
      item.css({'width':widthWrapperOuter,'height':"auto"});
      var pixels = -(itemBeforeActive*(widthWrapperOuter+15));
      item.parent().css(doTransform(pixels));
      item.parent().css({'width':wrapperWidthPhone+100});
      item.find(".image_block").css({'width':widthWrapperOuter,'height':widthWrapperOuter});
      itemActive.find('.documentDescription').css({'height':55});
      item.find(".portletItem").css({'height':widthWrapperOuter + 150})
      };
    };

  function next() {

    var widthWrapperOuter = base.width();
    var item = base.find(".qg-item");
    var itemActive = base.find(".qg-item.active");

    item.css(addTransition());
    item.find(".portletItem").css(addTransition());
    itemActive.css(addTransition());
    item.find(".image_block").css(addTransition());
    base.find('.qg-wrapper').css(addTransition());
    item.find(".documentDescription").css(addTransition());

    if ($(window).width() >= 768) {

      var activeWidth = widthWrapperOuter * 0.5875;
      var itemWidth = widthWrapperOuter * 0.175;
      var imageWidth = widthWrapperOuter * 0.38125;
      var itemWidthDescktop = widthWrapperOuter/5;

      if(itemActive.is(':last-child')) {
        itemActive.removeClass("active");
        item.first().addClass("active");
        var pixels = 0;
        base.find('.qg-wrapper').css(doTransform(pixels));
        base.find(".qg-item.active").css({'width':activeWidth});
        base.find('.qg-item:not(.active) .image_block').css({'width':itemWidth,'height':itemWidth});
        base.find('.qg-item.active .image_block').css({'width':imageWidth,'height':imageWidth});
        item.find(".documentDescription").css({'height':itemWidthDescktop/2-45});
        item.first().find('.documentDescription').css({'height':itemWidthDescktop-4});
        setTimeout(function(){
         base.find(".qg-item.active").nextAll().css({'width':itemWidth});
         },1000);
      } else {
        itemActive.next().css({'width':activeWidth});
        itemActive.next().find('.item_content').fadeIn();
        itemActive.css({'width':itemWidth});
        var pixels = (-item.index(itemActive)-1)*(itemWidth+30);
        item.parent().css(doTransform(pixels));
        itemActive.removeClass("active").next().addClass("active");
        base.find('.qg-item.active .image_block').css({'width':imageWidth,'height':imageWidth});
        itemActive.next().find('.documentDescription').css({'height':itemWidthDescktop-4});
        setTimeout(function(){
        base.find('.qg-item:not(.active) .image_block').css({'width':itemWidth,'height':itemWidth});
        base.find('.qg-item:not(.active) .documentDescription').css({'height':itemWidthDescktop/2-45});
        },1000);
      };
    } else if ($(window).width() >= 480) {
      if(itemActive.is(':last-child')) {
        itemActive.removeClass("active");
        item.first().addClass("active");
        var pixels = 0;
        base.find('.qg-wrapper').css( doTransform(pixels) );
      } else {
        itemActive.removeClass("active").next().addClass("active");
        var ind = base.find(itemActive).index()+1;
        var pixels = -widthWrapperOuter*ind;
        base.find('.qg-wrapper').css(doTransform(pixels));
      };
    } else {
      item.find('.documentDescription').css({'height':55});
      if(itemActive.is(':last-child')) {
        itemActive.removeClass("active");
        item.first().addClass("active");
        var pixels = 0;
        base.find('.qg-wrapper').css( doTransform(pixels) );
      } else {
        itemActive.removeClass("active").next().addClass("active");
        var ind = base.find(itemActive).index()+1;
        var pixels = (-widthWrapperOuter-15)*ind;
        base.find('.qg-wrapper').css(doTransform(pixels));
      };
    }
  }

  function prev() {

    var widthWrapperOuter = base.width();
    var item = base.find(".qg-item");
    var itemActive = base.find(".qg-item.active");

    item.css(addTransition());
    item.find(".portletItem").css(addTransition());
    itemActive.css(addTransition());
    base.find('.qg-wrapper').css(addTransition());
    item.find(".image_block").css(addTransition());
    item.find(".documentDescription").css(addTransition());

    if ($(window).width() >= 768) {

      var activeWidth = widthWrapperOuter * 0.5875;
      var itemWidth = widthWrapperOuter * 0.175;
      var imageWidth = widthWrapperOuter * 0.38125;
      var itemWidthDescktop = widthWrapperOuter/5;
      var wrapperWidthDescktop = (itemWidth+30) * (base.find(".qg-item").length+2);

      if(base.find(".qg-item.active").is(':first-child')) {
        base.find(".qg-item.active").removeClass("active");
        base.find(".qg-item").last().addClass("active");
        base.find(".qg-item").last().css({'width':activeWidth});
        base.find(".qg-item").first().css({'width':itemWidth});
        base.find('.qg-item:not(.active) .image_block').css({'width':itemWidth,'height':itemWidth});
        base.find('.documentDescription').css({'height':itemWidthDescktop/2-45});
        var pixels = -wrapperWidthDescktop+activeWidth+30;
        base.find('.qg-wrapper').css(doTransform(pixels));
        item.last().find('.documentDescription').css({'height':itemWidthDescktop-4});
        base.find('.qg-item.active .image_block').css({'width':imageWidth,'height':imageWidth});
      } else {
        base.find(".qg-item.active").prev().css({'width':activeWidth});
        base.find(".qg-item.active").css({'width':itemWidth});
        base.find(".qg-item.active").removeClass("active").prev().addClass("active");
        var pixels = -base.find(".qg-item").index(base.find(".qg-item.active"))*(itemWidth+30);
        base.find('.qg-wrapper').css(doTransform(pixels));
        base.find('.qg-item.active .image_block').css({'width':imageWidth,'height':imageWidth});
        base.find('.qg-item:not(.active) .image_block').css({'width':itemWidth,'height':itemWidth});
        itemActive.prev().find('.documentDescription').css({'height':itemWidthDescktop-4});
        base.find('.qg-item:not(.active) .documentDescription').css({'height':itemWidthDescktop/2-45});
      };
    } else if ($(window).width() >= 480) {
      var wrapperWidthPhone = widthWrapperOuter * (base.find(".qg-item").length);
      if(base.find(".qg-item.active").is(':first-child')) {
        base.find(".qg-item.active").removeClass("active");
        base.find(".qg-item").last().addClass("active");
        var pixels = -wrapperWidthPhone+widthWrapperOuter
        base.find('.qg-wrapper').css(doTransform(pixels));
      } else {
        base.find(".qg-item.active").removeClass("active").prev().addClass("active");
        var pixels = -base.find(".qg-item").index(base.find(".qg-item.active"))*widthWrapperOuter;
        base.find('.qg-wrapper').css(doTransform(pixels));
      };
      base.find(".qg-item").css({'width':widthWrapperOuter});
    } else {
      item.find('.documentDescription').css({'height':55});
      var wrapperWidthPhone = (widthWrapperOuter+15) * (base.find(".qg-item").length);
      console.log(widthWrapperOuter)
      if(base.find(".qg-item.active").is(':first-child')) {
        base.find(".qg-item.active").removeClass("active");
        base.find(".qg-item").last().addClass("active");
        var pixels = -wrapperWidthPhone+(widthWrapperOuter+15)
        base.find('.qg-wrapper').css(doTransform(pixels));
      } else {
        base.find(".qg-item.active").removeClass("active").prev().addClass("active");
        var pixels = -base.find(".qg-item").index(base.find(".qg-item.active"))*(widthWrapperOuter+15);
        base.find('.qg-wrapper').css(doTransform(pixels));
      };
      base.find(".qg-item").css({'width':widthWrapperOuter});
      };
  }

  function touchEffect() {

    var is_down = false, x_origine = 0, y_origine = 0;
    var widthWrapperOuter = base.find(".qg-carousel").width();
    var itemWidthDescktop = widthWrapperOuter/5;

    base.find(".qg-wrapper").on("touchstart", function(event) {

      x_origine = event.originalEvent.targetTouches[0].clientX;
      is_down = true;
      base.addClass("grabbing");

      $(window).on("touchmove", function(event) {

        var temp_x = event.originalEvent.changedTouches[0].clientX;
        var x_diff = temp_x - x_origine;

        if ( x_diff > 5 || x_diff < -5 ) {
          if(is_down){
            var tempPositionDesc = base.find(".qg-item.active").index() * (-base.find(".qg-item:not(active)").width()-30);
            var tempPositionPhone = base.find(".qg-item.active").index() * (-base.find(".qg-item:not(active)").width());
            base.find(".qg-wrapper").css(removeTransition())
            if ($(window).width() >= 768 ) {
              var pixels = x_diff+tempPositionDesc;
              base.find(".qg-wrapper").css({
                  '-webkit-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-moz-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-o-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-ms-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  'transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  "-webkit-transition": "all",
                  "-moz-transition": "all",
                  "transition": "all 0s"
              });
            } else {
              var pixels = x_diff+tempPositionPhone;
              base.find(".qg-wrapper").css({
                  '-webkit-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-moz-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-o-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  '-ms-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  'transform': 'translate3d('+ pixels +'px, 0px, 0px)',
                  "-webkit-transition": "all",
                  "-moz-transition": "all",
                  "transition": "all 0s"
                });
            }
            event.preventDefault();
          }
        };
      });
      
      $(window).bind("touchend", function(event) {
      if(is_down){
        var temp_x = event.originalEvent.changedTouches[0].clientX;
        base.find(".qg-wrapper").css(addTransition());
        is_down = false;  
        var wrapperWidth = base.find(".qg-wrapper-outer").width()/10;
        var itemWidth = base.find(".qg-wrapper-outer").width();
        var tempPosition = base.find(".qg-item.active").index() * (-base.find(".qg-item:not(active)").width()-30);
        if (temp_x - x_origine < 0) {
          if (-(temp_x - x_origine) < wrapperWidth) {
            if ($(window).width() >= 768 ) {
            base.find(".qg-wrapper").css({'left':tempPosition});
            } else { 
              var pixels = base.find(".qg-item.active").index() * (-base.find(".qg-item:not(active)").width());
              base.find(".qg-wrapper").css(doTransform(pixels));        
            }
          } else {
            next();
          };
        } else {
          if (temp_x - x_origine < wrapperWidth) {
            if ($(window).width() >= 768 ) {
            base.find(".qg-wrapper").css({'left':tempPosition});
            } else { 
              var pixels = base.find(".qg-item.active").index() * (-base.find(".qg-item:not(active)").width());
              base.find(".qg-wrapper").css(doTransform(pixels));         
            }
          } else {
            prev(); 
          }
        }
        base.removeClass("grabbing");
      }
    });
    });
  }

  function addTransition () {
    return {
      "-webkit-transition": "all " + 1 + "s ease",
      "-moz-transition": "all " + 1 + "s ease",
      "-o-transition": "all " + 1 + "s ease",
      "transition": "all " + 1 + "s ease"
    }
  };

  function removeTransition () {
    return {
      "-webkit-transition": "",
      "-moz-transition": "",
      "-o-transition": "",
      "transition": ""
    };
  };

  function doTransform (pixels) {
    return {
      '-webkit-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
      '-moz-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
      '-o-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
      '-ms-transform': 'translate3d('+ pixels +'px, 0px, 0px)',
      'transform': 'translate3d('+ pixels +'px, 0px, 0px)',
    }
  };

  base.find(".qg-next").click(function (event){
    $(".qg-item").stop();
    next();
  });

  base.find(".qg-prev").click(function (event){
    prev(); 
  });

  widthCalculate();
  touchEffect()

  $(window).resize(function() {
    widthCalculate();
    });
  }