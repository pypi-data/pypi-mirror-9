if (typeof Object.create !== "function") {
    Object.create = function (obj) {
        function F() {}
        F.prototype = obj;
        return new F();
    };
}
(function ($, window, document) {

    var Carousel = {
        init : function (options, el) {
            var base = this;

            base.$elem = $(el);
            base.options = $.extend({}, $.fn.qgCarousel.options, base.$elem.data(), options);

            base.userOptions = options;
            base.loadContent();
        },

        loadContent : function () {
            var base = this;
            base.$elem.css({opacity: 0});
            base.checkBrowser();
            base.wrapperWidth = 0;
            base.checkVisible = null;
            base.setVars();
        },

        setVars : function () {
            var base = this;
            if (base.$elem.children().length === 0) {return false; }
            base.eventTypes();
            base.$userItems = base.$elem.children();
            base.itemsAmount = base.$userItems.length;
            base.wrapItems();
            base.$qgItems = base.$elem.find(".qg-item");
            base.$qgWrapper = base.$elem.find(".qg-wrapper");
            base.currentItem = 0;
            base.onStartup();
        },

        onStartup : function () {
            var base = this;
            base.calculateItem();
            base.buildControls();
            base.response();
            base.moveEvents();

            base.$elem.find(".qg-wrapper").css("display", "block");

            if (!base.$elem.is(":visible")) {
                base.watchVisibility();
            } else {
                base.$elem.css("opacity", 1);
            }
            base.onstartup = false;     
        },

        updateVars : function () {
            var base = this;
            base.watchVisibility();
            base.calculateItem();
        },

        reload : function () {
            var base = this;
            window.setTimeout(function () {
                base.updateVars();
            }, 0);
        },

        response : function () {
            var base = this,
                smallDelay,
                lastWindowWidth;
            lastWindowWidth = $(window).width();

            base.resizer = function () {
                if ($(window).width() !== lastWindowWidth) {
                    window.clearTimeout(smallDelay);
                    smallDelay = window.setTimeout(function () {
                        lastWindowWidth = $(window).width();
                        base.updateVars();
                    });
                }
            };
            $(window).resize(base.resizer);
        },

        watchVisibility : function () {
            var base = this;
            if (base.$elem.is(":visible") === false) {
                base.$elem.css({opacity: 0});
                window.clearInterval(base.checkVisible);
            } else {
                return false;
            }
            base.checkVisible = window.setInterval(function () {
                if (base.$elem.is(":visible")) {
                    base.reload();
                    base.$elem.animate({opacity: 1}, 200);
                    window.clearInterval(base.checkVisible);
                }
            }, 500);
        },

        checkBrowser : function () {
            var base = this,
            		   isTouch,
            	ua = window.navigator.userAgent,
            	msie = ua.indexOf("MSIE ");

            base.$support3d = false;
            isTouch = "ontouchstart" in window || window.navigator.msMaxTouchPoints;

	        if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./)) {
				support3d = false;
	        } else {
	        	support3d = true;
	        };

            base.browser = {
                "support3d" : support3d,
                "isTouch" : isTouch
            };
        },

        wrapItems : function () {
            var base = this;
            base.$userItems.wrapAll("<div class=\"qg-wrapper\">");
            base.$elem.find(".qg-wrapper").wrap("<div class=\"qg-wrapper-outer\">");
            base.wrapperOuter = base.$elem.find(".qg-wrapper-outer");
            base.$elem.css("display", "block");
            base.$elem.find(".qg-item:first-child").addClass("active");
        },

        buildControls : function () {
            var base = this;
            if (base.options.navigation === true) {
                base.qgControls = $("<div class=\"qg-controls\"/>").toggleClass("clickable", !base.browser.isTouch).appendTo(base.$elem);
                base.buildButtons();
            }
        },

        buildButtons : function () {
            var base = this,
                buttonsWrapper = $("<div class=\"qg-buttons ng-collection-buttons\"/>");
            base.qgControls.append(buttonsWrapper);

            base.buttonPrev = $("<button/>", {
                "class" : "qg-prev",
                "html" : base.options.navigationText[0] || ""
            });

            base.buttonNext = $("<button/>", {
                "class" : "qg-next",
                "html" : base.options.navigationText[1] || ""
            });

            buttonsWrapper
                .append(base.buttonPrev)
                .append(base.buttonNext);

            buttonsWrapper.on("touchstart.qgControls mousedown.qgControls", "button[class^=\"qg\"]", function (event) {
                event.preventDefault();
            	base.$qgWrapper.css(
	            	base.addCssSpeed(base.options.slideSpeed)
	            	)
            });

            buttonsWrapper.on("touchend.qgControls mouseup.qgControls", "button[class^=\"qg\"]", function (event) {
                event.preventDefault();
                if ($(this).hasClass("qg-next")) {
                    base.next();
                } else {
                    base.prev();
                }
            });
        },

        calculateItem : function () {
            var base = this;

            base.calculateAllWidth();
            base.buildItem();
        },

        calculateAllWidth : function () {
            var base = this; 

            base.$widthWrapperOuter = base.$elem.width();
            base.$itemWidth = (base.$widthWrapperOuter - (base.options.columnGap*4)) / 5 + base.options.columnGap;
            base.$imageWidth = base.$itemWidth * 2 - base.options.columnGap;
        },

        buildItem : function () {
            var base = this;

            base.$pixelDesctop = -base.currentItem * base.$itemWidth;
            base.$pixelTablet = -base.currentItem * base.$widthWrapperOuter;
            base.$activeItem = base.$qgWrapper.find('.active');

            base.$qgWrapper.css( 
            	base.removeTransition()
            	)

            if ($(window).width() >= 768) {

                base.$qgWrapper.css({
                    'width': base.$itemWidth * (base.itemsAmount+3),
                    'height' : base.$itemWidth * 2
                    });
                base.transitionItemDesc();
                if (base.browser.support3d === true) {
                    base.$qgWrapper.css(
                    	base.doTranslate(base.$pixelDesctop)
                    	);
                } else {
                	base.$qgWrapper.animate({
                		'left' : base.$pixelDesctop
                		});
                }

            } else if ($(window).width() >= 480) {

                base.$qgWrapper.css({
                    'width': base.$widthWrapperOuter * (base.itemsAmount+1),
                    'height' : base.$widthWrapperOuter*2/3
                    });
                base.$qgItems.css({
                    'width': base.$widthWrapperOuter
                    });
                base.$qgItems.find(".image-block").css({
                    'width': base.$widthWrapperOuter*2/3,
                    'height': base.$widthWrapperOuter*2/3
                    });
                if (base.browser.support3d === true) {
                    base.$qgWrapper.css(
                    	base.doTranslate(base.$pixelTablet)
                    	);
                } else {
                	base.$qgWrapper.animate({
                		'left' : base.$pixelTablet
                		});
                }

            } else {

                base.$qgWrapper.css({
                    'width': base.$widthWrapperOuter * (base.itemsAmount+1),
                    'height': base.$widthWrapperOuter + base.$widthWrapperOuter*1/2
                    });
                base.$qgItems.css({
                    'width': base.$widthWrapperOuter
                    });
                 base.$qgItems.find(".image-block").css({
                    'width': base.$widthWrapperOuter,
                    'height': base.$widthWrapperOuter
                    });
                if (base.browser.support3d === true) {
                    base.$qgWrapper.css(
                    	base.doTranslate(base.$pixelTablet)
                    	);
                } else {
                	base.$qgWrapper.animate({
                		'left' : base.$pixelTablet
                		});
                }
            };
        },

        next : function () {
            var base = this;

            if (base.isTransition) {
                return false;
            }

            if (base.currentItem == base.itemsAmount - 1 ) {
                
                base.currentItem = 0;
                base.$elem.find(".qg-item.active").removeClass("active");
                base.$qgItems.first().addClass("active");

                if (base.browser.support3d === true) {
                    base.transition3d();
                } else {
                	base.css2move();
                }
            } else {
            	
                base.currentItem += 1;
                base.$elem.find(".qg-item.active").removeClass("active").next().addClass("active");

                if (base.browser.support3d === true) {
                    base.transition3d();
                } else {
                	base.css2move();
                }
            };
        },

        prev : function () {
            var base = this;

            if (base.isTransition) {
                return false;
            }

            if (base.currentItem == 0 ) {

                base.currentItem = base.itemsAmount-1;
                base.$elem.find(".qg-item.active").removeClass("active");
                base.$elem.find(".qg-item").last().addClass("active");

                if (base.browser.support3d === true) {
                    base.transition3d();
                } else {
                	base.css2move();
                }
            } else {

                base.currentItem -= 1;
				base.$elem.find(".qg-item.active").removeClass("active").prev().addClass("active");

                if (base.browser.support3d === true) {
                    base.transition3d();
                } else {
                	base.css2move();
                }
            };

        },

        addCssSpeed : function (speed) {
            return {
                "-webkit-transition": "all " + speed + "ms ease",
                "-moz-transition": "all " + speed + "ms ease",
                "-o-transition": "all " + speed + "ms ease",
                "transition": "all " + speed + "ms ease"
            };
        },

        removeTransition : function () {
            return {
                "-webkit-transition": "",
                "-moz-transition": "",
                "-o-transition": "",
                "transition": ""
            };
        },

        doTranslate : function (pixels) {
            return {
                "-webkit-transform": "translate3d(" + pixels + "px, 0px, 0px)",
                "-moz-transform": "translate3d(" + pixels + "px, 0px, 0px)",
                "-o-transform": "translate3d(" + pixels + "px, 0px, 0px)",
                "-ms-transform": "translate3d(" + pixels + "px, 0px, 0px)",
                "transform": "translate3d(" + pixels + "px, 0px,0px)"
            };
        },

        transitionItemDesc : function () {
        	var base = this;

        	base.$qgItems.css({
                'width': base.$itemWidth,
                '-webkit-transition' : 'width',
				'transition' : 'width'
                });
            base.$qgItems.find(".image-block").css({
                'width': base.$itemWidth-base.options.columnGap,
                'height': base.$itemWidth-base.options.columnGap
                });
            base.$elem.find(".qg-item.active").css({
                'width': base.$itemWidth*3 - base.options.columnGap,
                '-webkit-transition' : 'width',
				'transition' : 'width'
                });
            base.$elem.find(".qg-item.active").find(".image-block").css({
                'width': base.$imageWidth,
                'height': base.$imageWidth
                });
        },

        transition3d : function () {
            var base = this;

            base.$pixelDesctop = -base.currentItem * base.$itemWidth;
            base.$pixelTablet = -base.currentItem * base.$widthWrapperOuter;
            
            if ($(window).width() >= 768) {
                base.$qgWrapper.css(
                	base.doTranslate(base.$pixelDesctop)
                	);
               	base.transitionItemDesc();
            } else if ($(window).width() >= 480) {
                base.$qgWrapper.css(
                	base.doTranslate(base.$pixelTablet)
                	);
            } else {
                base.$qgWrapper.css(
                	base.doTranslate(base.$pixelTablet)
                	);
            };
        },

        css2move : function () {
            var base = this;

            base.$pixelDesctop = -base.currentItem * base.$itemWidth;
            base.$pixelTablet = -base.currentItem * base.$widthWrapperOuter;

 			base.isCssFinish = false;

            if ($(window).width() >= 768) {
                base.$qgWrapper.animate({
                	"left" : base.$pixelDesctop 
                },600, "swing");
                base.css2ItemDesc();
            } else if ($(window).width() >= 480) {
                base.$qgWrapper.stop(true, true).animate({
                	"left" : base.$pixelTablet 
                });
            } else {
                base.$qgWrapper.stop(true, true).animate({
                	"left" : base.$pixelTablet 
                });
            };
        },

		css2ItemDesc : function () { 
			var base = this;

        	base.$qgItems.animate({
                'width': base.$itemWidth,
                },600, "swing");
        	            base.$elem.find(".qg-item.active").animate({
                'width': base.$itemWidth*3,
                },600, "swing");
            base.$qgItems.find(".image-block").animate({
                'width': base.$itemWidth-base.options.columnGap,
                'height': base.$itemWidth-base.options.columnGap
                },600, "swing");

            base.$elem.find(".qg-item.active").find(".image-block").animate({
                'width': base.$imageWidth,
                'height': base.$imageWidth
                },600, "swing");
		},

//******** touch event

        moveEvents : function () {
            var base = this;
            if (base.options.mouseDrag !== false || base.options.touchDrag !== false) {
                base.gestures();
            }
        },

		eventTypes : function () {
            var base = this,
                types = ["s", "e", "x"];

            base.ev_types = {};

            if (base.options.mouseDrag === true && base.options.touchDrag === true) {
                types = [
                    "touchstart.qg mousedown.qg",
                    "touchmove.qg mousemove.qg",
                    "touchend.qg touchcancel.qg mouseup.qg"
                ];
            } else if (base.options.mouseDrag === false && base.options.touchDrag === true) {
                types = [
                    "touchstart.qg",
                    "touchmove.qg",
                    "touchend.qg touchcancel.qg"
                ];
            } else if (base.options.mouseDrag === true && base.options.touchDrag === false) {
                types = [
                    "mousedown.qg",
                    "mousemove.qg",
                    "mouseup.qg"
                ];
            }

            base.ev_types.start = types[0];
            base.ev_types.move = types[1];
            base.ev_types.end = types[2];
        	
        },

 		gestures : function () {
 			var base = this,
 				is_down = false,
 				is_move = false,
 			    locals = {
                    offsetX : 0,
                    offsetY : 0,
                    relativePos : 0,
                    position: null,
                    sliding : null,
                    dragging: null,
                    targetElement : null,
                    dragDirection : null
                };

            base.isCssFinish = true;

            function getTouches(event) {
                if (event.touches !== undefined) {
                    return {
                        x : event.touches[0].pageX,
                        y : event.touches[0].pageY
                    };
                }
                if (event.touches === undefined) {
                    if (event.pageX !== undefined) {
                        return {
                            x : event.pageX,
                            y : event.pageY
                        };
                    }
                    if (event.pageX === undefined) {
                        return {
                            x : event.clientX,
                            y : event.clientY
                        };
                    }
                }
            }

 			function swapEvents(type) {
                if (type === "on") {
                    $(document).on(base.ev_types.move, dragMove);
                    $(document).on(base.ev_types.end, dragEnd);
                } else if (type === "off") {
                    $(document).off(base.ev_types.move);
                    $(document).off(base.ev_types.end);
                }
            }

            function dragStart(event) {
            	var ev = event.originalEvent || event || window.event,
                    position;

                base.newPosX = 0;
                base.newRelativeX = 0;
                
                $(this).css(base.removeTransition());

                position = $(this).position();
                locals.relativePos = position.left;

                locals.offsetX = getTouches(ev).x - position.left;
                locals.offsetY = getTouches(ev).y - position.top;

                swapEvents("on");

                locals.sliding = false;
                locals.targetElement = ev.target || ev.srcElement;
            	}

            function dragMove(event) {
				var ev = event.originalEvent || event || window.event;

				base.newPosX = getTouches(ev).x - locals.offsetX;
                base.newPosY = getTouches(ev).y - locals.offsetY;
                base.newRelativeX = base.newPosX - locals.relativePos;
                base.tempPositionDesc = base.$pixelDesctop + base.newRelativeX;
                base.tempPositionTablets = base.$pixelTablet + base.newRelativeX;

                if (base.newRelativeX > 8 || base.newRelativeX < -8) {
                    if (ev.preventDefault !== undefined) {
                        ev.preventDefault();
                    } else {
                        ev.returnValue = false;
                    }
                    locals.sliding = true;
                }

                if ((base.newPosY > 10 || base.newPosY < -10) && locals.sliding === false) {
                    $(document).off("touchmove.qg");
                }

                if ($(window).width() >= 768) {
	                if (base.browser.support3d === true) {
	                    base.$qgWrapper.css(
	                    	base.doTranslate(base.tempPositionDesc)
	                    	);
	                } else {
	                	base.$qgWrapper.css({
		                    'left':  base.tempPositionDesc
		                	});
	                	}
				} else {
		            if (base.browser.support3d === true) {
						base.$qgWrapper.css(
							base.doTranslate(base.tempPositionTablets)
							);
	                } else {
	                	base.$qgWrapper.css({
		                    'left': base.tempPositionTablets
		                	});
	                	}
					};
            	}

            function dragEnd(event) {
             	var ev = event.originalEvent || event || window.event,
                    newPosition,
                    handlers,
                    qgStopEvent;

                ev.target = ev.target || ev.srcElement;
                locals.dragging = false;

                base.$qgWrapper.css(
	            	base.addCssSpeed(base.options.slideSpeed)
	            	)
 				if (base.newRelativeX !== 0) {

	 				if (base.newRelativeX < 0) {
	                    base.dragDirection = locals.dragDirection = "left";
	                    base.next();
	                } else {
	                    base.dragDirection = locals.dragDirection = "right";
	                    base.prev();
	                }

                    if (locals.targetElement === ev.target) {
                        $(ev.target).on("click.disable", function (ev) {
                            ev.preventDefault();
                            $(ev.target).off("click.disable");
                        });
                        handlers = $.data(ev.target, "events").click;
                        qgStopEvent = handlers.pop();
                        handlers.splice(0, 0, qgStopEvent);
                    }	
            	}
            	swapEvents("off");
            }
            base.$elem.on(base.ev_types.start, ".qg-wrapper", dragStart);
 		},
    };

    $.fn.qgCarousel = function (options) {
        return this.each(function () {
            if ($(this).data("qg-init") === true) {
                return false;
            }
            $(this).data("qg-init", true);
            var carousel = Object.create(Carousel);
            carousel.init(options, this);
            $.data(this, "qgCarousel", carousel);
        });
    };

    $.fn.qgCarousel.options = {

        navigation : true,
        navigationText : ["prev", "next"],
        slideSpeed : 1000,

        mouseDrag : false,
        touchDrag : true,
        columnGap : 30,

    };
}(jQuery, window, document));