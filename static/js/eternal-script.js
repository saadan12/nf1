/* Rina-pen  https://codepen.io/rinatoptimus/pen/MbZepR*/
(function($){

  $.fn.makeRollingCaption = function(options) {

    options = $.extend({
      speed: 20
    }, options);

    this.each(function(index, container){

      var methods = {

        initialize: function() {

          this.container = $(container).first();
          this.content = this.container.find('.b-rolling-caption__content-rina-pen');
          this.wrap = this.container.find('.b-rolling-caption__wrap-rina-pen');

          this.setWidth();
          this.wrap.show();

          var item = this.content.find('span').first();

          this.start(item);

          $(window).on('resize', $.proxy(function(){
            this.content.stop(true, true).css('left', 0);
            if ( this.timer ) clearTimeout(this.timer); else this.wrap.hide();
            this.timer = setTimeout($.proxy(this.onStopResize, this), 300);

          }, this));

        },

        setWidth: function() {
          this.wrap.width(this.container.parent().width());
        },

        onStopResize: function() {

          this.setWidth();

          this.timer = null;
          this.wrap.show();
          this.start(this.content.find('span').first());
        },

        start: function(item) {
          if ( item.length ) {

            this.content.animate({
              left: '-=' + item.width() + 'px'
            }, item.width() * options.speed, 'linear', $.proxy(function(){
              var next = item.next();
              if ( !next ) next = this.content.find('span').first();
              this.content.append(item);
              if ( !this.timer ) {
                this.content.css('left', 0);
                this.start(next);
              }

            }, this));

          }
        }

      };

      methods.initialize();

    });

  };

})(jQuery);


$(function(){
  $('#rolling-caption-rina-pen').makeRollingCaption({ speed: 20 });
});


// VIDEO PLAYER LIGHTBOX PEN
// https://codepen.io/darcyvoutt/pen/MaamWg


// Function to reveal lightbox and adding YouTube autoplay
function revealVideo(div,video_id) {
  var video = document.getElementById(video_id).src;
  document.getElementById(video_id).src = video+'&autoplay=1'; // adding autoplay to the URL
  document.getElementById(div).style.display = 'block';
}

// Hiding the lightbox and removing YouTube autoplay
function hideVideo(div,video_id) {
  var video = document.getElementById(video_id).src;
  var cleaned = video.replace('&autoplay=1',''); // removing autoplay form url
  document.getElementById(video_id).src = cleaned;
  document.getElementById(div).style.display = 'none';
}




/* Button Video Player https://codepen.io/JacobLett/pen/zEJwpN*/

// $(document).ready(function() {
//   // Gets the video src from the data-src on each button
//   var $videoSrc;
//   $(".video-btn-jacob-pen").click(function() {
//     $videoSrc = $(this).attr("data-src");
//     console.log("button clicked " + $videoSrc);
//   });
//
//   // when the modal is opened autoplay it
//   $("#myModal-jacob-pen").on("shown.bs.modal", function(e) {
//     console.log("modal opened " + $videoSrc);
//     // set the video src to autoplay and not to show related video. Youtube related video is like a box of chocolates... you never know what you're gonna get
//     $("#video-jacob-pen").attr(
//       "src",
//       $videoSrc + "?autoplay=1&showinfo=0&modestbranding=1&rel=0&mute=0"
//     );
//   });
//
//   // stop playing the youtube video when I close the modal
//   $("#myModal-jacob-pen").on("hide.bs.modal", function(e) {
//     // a poor man's stop video
//     $("#video-jacob-pen").attr("src", $videoSrc);
//   });
//
//   // document ready
// });
