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
      _print(_safe('<p> Time: '));
    
      _print(this.name);
    
      _print(_safe('</p>\n<table>\n    <tr>\n        <td>\n          count\n        </td>\n        <td>\n          '));
    
      _print(this.count);
    
      _print(_safe('\n        </td>\n    </tr>\n    <tr>\n        <td>\n          unique\n        </td>\n        <td>\n          '));
    
      _print(this.unique);
    
      _print(_safe('\n        </td>\n    </tr>   \n    <tr>\n        <td>\n          first\n        </td>\n        <td>\n          '));
    
      _print(this.first);
    
      _print(_safe('\n        </td>\n    </tr>   \n    <tr>\n        <td>\n          last\n        </td>\n        <td>\n          '));
    
      _print(this.last);
    
      _print(_safe('\n        </td>\n    </tr>   \n    \n</table>\n'));
    
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
