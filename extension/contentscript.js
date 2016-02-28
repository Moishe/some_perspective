/**
 * Parses text from Twitter's API and generates a bar with trending topics at
 * the top of the current page
 *
 * @param data Object JSON decoded response.  Null if the request failed.
 */
function onText(data) {
  if (!data) {
    return;
  }

  // Create the overlay at the top of the page and fill it with data.
  var trends_dom = document.createElement('div');
  trends_dom.setAttribute("id", "trends");
  var title_dom = document.createElement('strong');
  title_dom.innerText = data;
  trends_dom.appendChild(title_dom);
  trends_dom.style.cssText = [
    'background-color: #ffd700;',
    'background-image: -webkit-repeating-linear-gradient(' +
        '45deg, transparent, transparent 35px,' +
        'rgba(0,0,0,.1) 35px, rgba(0,0,0,.1) 70px);',
    'color: #000;',
    'padding: 10px;',
    'font: 14px Arial;'
  ].join(' ');
  document.body.style.cssText = 'position: relative';
  document.body.parentElement.insertBefore(trends_dom, document.body);
};

function countWords() {
  var wordcount = {};
  var types = ['div', 'p', 'td'];
  var triggered = false;
  for (var i = 0; i < types.length; i++) {
    t = types[i];
    $(t).each(function(idx) {
      var text = $(this).text();
      for (var j = 0; j < keywords.length; j++) {
        if (text.indexOf(keywords[j]) > 0) {
          if (!triggered) {
            onText("EMERGENCY OVERRIDE THIS IS THE WORST");
            triggered = true;
          }
        }
      }
      var words = text.match(/(\w+)/g);
      if (words) {
        for (var j = 0; j < words.length; j++) {
          word = words[j];
          if (wordcount[word]) {
            wordcount[word] += 1;
          } else {
            wordcount[word] = 1;
          }
        }
      }
    });
  }
  $.ajax({
    type: "POST",
    url: "http://localhost:8080/words",
    data: {
      'words': JSON.stringify(wordcount), 
      'url': window.location.hostname // TODO: this should probably just be a hash
    },
    success: function(result) {
      onText(result);
    }
  });
}

countWords();

