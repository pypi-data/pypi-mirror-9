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
      _print(_safe('<div class="bk-bs-panel-heading bk-crossfilter-panel-heading">\n  Factor: '));
    
      _print(this.name);
    
      _print(_safe('\n</div>\n<div class="bk-bs-panel-body">\n  <table class="bk-table">\n    <tbody>\n      <tr>\n        <td>\n          count\n        </td>\n        <td>\n          '));
    
      _print(this.count);
    
      _print(_safe('\n        </td>\n      </tr>\n      <tr>\n        <td>\n          unique\n        </td>\n        <td>\n          '));
    
      _print(this.unique);
    
      _print(_safe('\n        </td>\n      </tr>\n      <tr>\n        <td>\n          top\n        </td>\n        <td>\n          '));
    
      _print(this.top);
    
      _print(_safe('\n        </td>\n      </tr>\n      <tr>\n        <td>\n          freq\n        </td>\n        <td>\n          '));
    
      _print(this.freq);
    
      _print(_safe('\n        </td>\n      </tr>\n    </tbody>\n  </table>\n</div>\n</div>\n'));
    
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
