document.addEventListener('DOMContentLoaded', function() {
  var years = document.getElementsByClassName('year');
  for(var i = 0; i < years.length; ++i) {
    var year = years[i];
    year.getElementsByTagName('span')[0].onclick = function(year) { return function() {
      if(year.classList.contains('displayed')) {
        year.classList.remove('displayed');
      } else {
        year.classList.add('displayed');
      }
    }; }(year);
  }
  
  var months = document.getElementsByClassName('month');
  for(var i = 0; i < months.length; ++i) {
    var month = months[i];
    month.getElementsByTagName('span')[0].onclick = function(month) { return function() {
      if(month.classList.contains('displayed')) {
        month.classList.remove('displayed');
      } else {
        month.classList.add('displayed');
        setTimeout(function() {
          month.scrollIntoView(true);
        }, 300);
      }
    }; }(month);
  }
});
