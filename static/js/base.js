document.addEventListener('DOMContentLoaded', function() {
  var nav = document.getElementsByTagName('main')[0]
                    .getElementsByTagName('nav')[0];
  var links = nav.getElementsByClassName('links')[0];
  var right_arrow = nav.getElementsByClassName('right-arrow')[0];
  var left_arrow = nav.getElementsByClassName('left-arrow')[0];

  right_arrow.addEventListener('click', function() {
    links.classList.add('hidden');
    right_arrow.classList.add('hidden');
    left_arrow.classList.remove('hidden');
  });

  left_arrow.addEventListener('click', function() {
    links.classList.remove('hidden');
    right_arrow.classList.remove('hidden');
    left_arrow.classList.add('hidden');
  });
});
