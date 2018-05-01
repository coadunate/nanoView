// Try to read a range out of the URL. This is helpful for testing.
// function getParameterByName(name) {
//   name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
//   var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
//       results = regex.exec(location.search);
//   return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
// }
// var pos = getParameterByName('pos');
//
// if (pos) {
//   var m = /(.*):([0-9,]+)-([0-9,]+)/.exec(pos);
//   if (!m) { throw 'Invalid range: ' + pos; }
//   var makeNum = function(x) { return Number(x.replace(/,/g, '')); };
//   range = {contig: m[1], start: makeNum(m[2]), stop: makeNum(m[3])};
// } else {
//   // use default range from, e.g. data.js
// }
//
// var colorByStrand = getParameterByName('colorByStrand');
// if (colorByStrand) {
//   sources.forEach(source => {
//     if (source.viz.options) {
//       source.viz.options.colorByStrand = true;
//     }
//   });
// }
var p = pileup.create(document.getElementById('pileup'), {
  range: range,
  tracks: sources
});
