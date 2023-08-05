define(function(){
  var template = function(__obj) {
  var _safe = function(value) {
    if (typeof value === 'undefined' && value == null)
      value = '';
    var result = new String(value);
    result.ecoSafe = true;
    return result;
  };
  return (function() {
    var __out = [], __self = this, _print = function(value) {
      if (typeof value !== 'undefined' && value != null)
        __out.push(value.ecoSafe ? value : __self.escape(value));
    }, _capture = function(callback) {
      var out = __out, result;
      __out = [];
      callback.call(this);
      result = __out.join('');
      __out = out;
      return _safe(result);
    };
    (function() {
      _print(_safe('<div class="bk-crossfilter-container">\n  <table>\n    <tr>\n      <td class="aligntable">\n        <div class="bk-crossfilter-configuration bk-bs-container">\n          <div class="bk-crossfilter-row">\n            <div class="col-md-4 bk-column-list">\n            </div>\n            <div class="col-md-5 bk-filters-facets">\n              <div class="bk-bs-panel bk-bs-panel-primary bk-filters">\n                <div class="bk-bs-panel-heading bk-crossfilter-panel-heading">\n                  Filter\n                </div>\n                <div class="bk-bs-panel-body bk-filters-selections">\n                </div>\n              </div>\n              <div class="bk-bs-panel bk-bs-panel-primary bk-facet bk-facet-x">\n                <div class="bk-bs-panel-heading bk-crossfilter-panel-heading">\n                  Facet X\n                </div>\n                <div class="bk-facets-selections ">\n                </div>\n              </div>\n              <div class="bk-bs-panel bk-bs-panel-primary bk-facet bk-facet-y">\n                <div class="bk-bs-panel-heading bk-crossfilter-panel-heading">\n                  Facet Y\n                </div>\n                <div class="bk-facets-selections ">\n                </div>\n              </div>\n              <div class="bk-bs-panel bk-bs-panel-primary bk-facet bk-facet-tab">\n                <div class="bk-bs-panel-heading bk-crossfilter-panel-heading">\n                  Facet Tab (Coming Soon)\n                </div>\n                <div class="bk-facets-selections ">\n                </div>\n              </div>\n            </div>\n            <div class="col-md-3 bk-plot-selection">\n              <form class="bk-widget-form">\n                <div class="bk-plot-selector">\n                </div>\n                <div class="bk-x-selector">\n                </div>\n                <div class="bk-y-selector">\n                </div>\n                <div class="bk-agg-selector">\n                </div>\n              </form>\n            </div>\n          </div>\n        </div>\n      </td>\n      <td class="aligntable">\n        <div class="bk-plot">\n        </div>\n      </td>\n    </tr>\n  </table>\n</div>\n'));
    
    }).call(this);
    
    return __out.join('');
  }).call((function() {
    var obj = {
      escape: function(value) {
        return ('' + value)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;');
      },
      safe: _safe
    }, key;
    for (key in __obj) obj[key] = __obj[key];
    return obj;
  })());
};
  return template;
});
