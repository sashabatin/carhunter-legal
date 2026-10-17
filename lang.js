// Language choice. The root page sends a first-time visitor to their browser language;
// a click on the language switcher is remembered, so a reader who picked English stays there.
(function () {
  var KEY = 'chw_lang';
  var PAGES = { ru: '/ru/', ka: '/ka/', fa: '/fa/' };
  function load() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-lang]');
    if (a) save(a.getAttribute('data-lang'));
  });

  if (document.documentElement.getAttribute('data-autolang') === '1' && !load()) {
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    var target = PAGES[nav.slice(0, 2).toLowerCase()];
    if (target) location.replace(target);
  }
})();
