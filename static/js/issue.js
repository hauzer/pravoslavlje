function throttle(wait, fn) {
  var time = Date.now();
  return function() {
    if (Date.now() - time + wait >= 0) {
      fn();
      time = Date.now();
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var pdfs = document.getElementsByClassName('pdf');
  var pdf = null;
  for(var i = 0; i < pdfs.length; ++i) {
    if(pdfs[i].offsetParent) {
      pdf = pdfs[i];
      break;
    }
  }

  if(pdf) {
    var last_scroll = 0;
    var fn = function() {
      var rect = pdf.getBoundingClientRect();
      var view_treshold = pdf.clientHeight * 0.125;
      var is_in_view = rect.top >= -view_treshold && rect.bottom <= window.innerHeight + view_treshold;
      var is_zoomed = document.body.classList.contains('zoomed');

      if(!is_zoomed && is_in_view) {
        setTimeout(function() {
          if(Date.now() - last_scroll >= 400) {
            document.body.classList.add('zoomed');
            setTimeout(function() {
              pdf.scrollIntoView(true);
            }, 400);
          }
        }, 400);
      } else if(is_zoomed && !is_in_view) {
        document.body.classList.remove('zoomed');
      }

      last_scroll = Date.now();
    };

    window.addEventListener('scroll', throttle(100, fn));
    window.addEventListener('load', fn);
  }
});
