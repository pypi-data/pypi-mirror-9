(function() {
  define(["underscore", "sprintf", "numeral"], function(_, sprintf, Numeral) {
    var replace_placeholders, _format_number;
    _format_number = function(number) {
      if (_.isString(number)) {
        return number;
      }
      if (Math.floor(number) === number) {
        return sprintf("%d", number);
      }
      if (Math.abs(number) > 0.1 && Math.abs(number) < 1000) {
        return sprintf("%0.3f", number);
      }
      return sprintf("%0.3e", number);
    };
    replace_placeholders = function(string, data_source, i, special_vars) {
      var _this = this;
      if (special_vars == null) {
        special_vars = {};
      }
      string = string.replace(/(^|[^\$])\$(\w+)/g, function(match, prefix, name) {
        var replacement;
        replacement = (function() {
          switch (name) {
            case "index":
              return "" + i;
            case "x":
              return "" + (_format_number(x));
            case "y":
              return "" + (_format_number(y));
            case "vx":
              return "" + vx;
            case "vy":
              return "" + vy;
            case "sx":
              return "" + sx;
            case "sy":
              return "" + sy;
          }
        })();
        if (replacement != null) {
          return "" + prefix + replacement;
        } else {
          return match;
        }
      });
      string = string.replace(/(^|[^@])@(?:(\$?\w+)|{([^{}]+)})(?:{([^{}]+)})?/g, function(match, prefix, name, long_name, format) {
        var column, replacement, value;
        name = long_name != null ? long_name : name;
        value = name[0] === "$" ? special_vars[name.substring(1)] : (column = data_source.get_column(name), column != null ? column[i] : special_vars[name]);
        replacement = value == null ? "???" : format != null ? Numeral.format(value, format) : _format_number(value);
        return "" + prefix + (_.escape(replacement));
      });
      return string;
    };
    return {
      replace_placeholders: replace_placeholders
    };
  });

}).call(this);

/*
//@ sourceMappingURL=util.js.map
*/