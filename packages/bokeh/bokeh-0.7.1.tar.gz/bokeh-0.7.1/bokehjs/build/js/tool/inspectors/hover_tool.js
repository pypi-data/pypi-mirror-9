(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "sprintf", "common/collection", "renderer/annotation/tooltip", "./inspect_tool", "numeral"], function(_, sprintf, Collection, Tooltip, InspectTool, Numeral) {
    var HoverTool, HoverToolView, HoverTools, _color_to_hex, _format_number, _ref, _ref1, _ref2;
    _color_to_hex = function(color) {
      var blue, digits, green, red, rgb;
      if (color.substr(0, 1) === '#') {
        return color;
      }
      digits = /(.*?)rgb\((\d+), (\d+), (\d+)\)/.exec(color);
      red = parseInt(digits[2]);
      green = parseInt(digits[3]);
      blue = parseInt(digits[4]);
      rgb = blue | (green << 8) | (red << 16);
      return digits[1] + '#' + rgb.toString(16);
    };
    _format_number = function(number) {
      if (typeof number === "string") {
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
    HoverToolView = (function(_super) {
      __extends(HoverToolView, _super);

      function HoverToolView() {
        _ref = HoverToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      HoverToolView.prototype.bind_bokeh_events = function() {
        var r, _i, _len, _ref1;
        _ref1 = this.mget('renderers');
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          r = _ref1[_i];
          this.listenTo(r.get('data_source'), 'inspect', this._update);
        }
        return this.plot_view.canvas_view.canvas_wrapper.css('cursor', 'crosshair');
      };

      HoverToolView.prototype._move = function(e) {
        var canvas, rid, tt, vx, vy, _ref1;
        if (!this.mget('active')) {
          return;
        }
        canvas = this.plot_view.canvas;
        vx = canvas.sx_to_vx(e.bokeh.sx);
        vy = canvas.sy_to_vy(e.bokeh.sy);
        if (!this.plot_view.frame.contains(vx, vy)) {
          _ref1 = this.mget('ttmodels');
          for (rid in _ref1) {
            tt = _ref1[rid];
            tt.clear();
          }
          return;
        }
        return this._inspect(vx, vy);
      };

      HoverToolView.prototype._move_exit = function() {
        var rid, tt, _ref1, _results;
        _ref1 = this.mget('ttmodels');
        _results = [];
        for (rid in _ref1) {
          tt = _ref1[rid];
          _results.push(tt.clear());
        }
        return _results;
      };

      HoverToolView.prototype._inspect = function(vx, vy, e) {
        var geometry, r, sm, _i, _len, _ref1;
        geometry = {
          type: 'point',
          vx: vx,
          vy: vy
        };
        _ref1 = this.mget('renderers');
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          r = _ref1[_i];
          sm = r.get('data_source').get('selection_manager');
          sm.inspect(this, this.plot_view.renderers[r.id], geometry, {
            "geometry": geometry
          });
        }
      };

      HoverToolView.prototype._update = function(indices, tool, renderer, ds, _arg) {
        var canvas, colname, color, column, frame, geometry, hex, i, label, match, opts, row, rx, ry, span, swatch, sx, sy, table, td, tooltip, value, vx, vy, x, xmapper, y, ymapper, _i, _j, _len, _len1, _ref1, _ref2, _ref3, _ref4, _ref5,
          _this = this;
        geometry = _arg.geometry;
        tooltip = (_ref1 = this.mget('ttmodels')[renderer.model.id]) != null ? _ref1 : null;
        if (tooltip == null) {
          return;
        }
        tooltip.clear();
        if (indices.length === 0) {
          return;
        }
        vx = geometry.vx;
        vy = geometry.vy;
        canvas = this.plot_model.get('canvas');
        frame = this.plot_model.get('frame');
        sx = canvas.vx_to_sx(vx);
        sy = canvas.vy_to_sy(vy);
        xmapper = frame.get('x_mappers')[renderer.mget('x_range_name')];
        ymapper = frame.get('y_mappers')[renderer.mget('y_range_name')];
        x = xmapper.map_from_target(vx);
        y = ymapper.map_from_target(vy);
        for (_i = 0, _len = indices.length; _i < _len; _i++) {
          i = indices[_i];
          if (this.mget('snap_to_data') && (renderer.glyph.sx != null) && (renderer.glyph.sy != null)) {
            rx = canvas.sx_to_vx(renderer.glyph.sx[i]);
            ry = canvas.sy_to_vy(renderer.glyph.sy[i]);
          } else {
            _ref2 = [vx, vy], rx = _ref2[0], ry = _ref2[1];
          }
          table = $('<table></table>');
          _ref3 = this.mget("tooltips");
          for (_j = 0, _len1 = _ref3.length; _j < _len1; _j++) {
            _ref4 = _ref3[_j], label = _ref4[0], value = _ref4[1];
            row = $("<tr></tr>");
            row.append($("<td class='bk-tooltip-row-label'>" + label + ": </td>"));
            td = $("<td class='bk-tooltip-row-value'></td>");
            if (value.indexOf("$color") >= 0) {
              _ref5 = value.match(/\$color(\[.*\])?:(\w*)/), match = _ref5[0], opts = _ref5[1], colname = _ref5[2];
              column = ds.get_column(colname);
              if (column == null) {
                span = $("<span>" + colname + " unknown</span>");
                td.append(span);
                continue;
              }
              hex = (opts != null ? opts.indexOf("hex") : void 0) >= 0;
              swatch = (opts != null ? opts.indexOf("swatch") : void 0) >= 0;
              color = column[i];
              if (color == null) {
                span = $("<span>(null)</span>");
                td.append(span);
                continue;
              }
              if (hex) {
                color = _color_to_hex(color);
              }
              span = $("<span>" + color + "</span>");
              td.append(span);
              if (swatch) {
                span = $("<span class='bk-tooltip-color-block'> </span>");
                span.css({
                  backgroundColor: color
                });
              }
              td.append(span);
            } else {
              value = value.replace(/(^|[^\$])\$(\w+)/g, function(match, prefix, name) {
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
              value = value.replace(/(^|[^@])@(?:(\w+)|{([^{}]+)})(?:{([^{}]+)})?/g, function(match, prefix, name, long_name, format) {
                var replacement;
                name = long_name != null ? long_name : name;
                column = ds.get_column(name);
                replacement = column == null ? "" + name + " unknown" : (value = column[i], format != null ? Numeral(value).format(format) : _.isNumber(value) ? _format_number(value) : value);
                return "" + prefix + replacement;
              });
              span = $('<span>').text(value);
              td.append(span);
            }
            row.append(td);
            table.append(row);
          }
          tooltip.add(rx, ry, table);
        }
        return null;
      };

      return HoverToolView;

    })(InspectTool.View);
    HoverTool = (function(_super) {
      var icon;

      __extends(HoverTool, _super);

      function HoverTool() {
        _ref1 = HoverTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      HoverTool.prototype.default_view = HoverToolView;

      HoverTool.prototype.type = "HoverTool";

      HoverTool.prototype.tool_name = "Hover Tool";

      icon = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA8ElEQVQ4T42T0Q2CMBCGaQjPxgmMG/jelIQN3ECZQEfADRwBJzBuQCC81wlkBHxvqP8lmhTsUfpSWvp/vfvvKiJn1HVdpml6dPdC38I90DSNxVobYzKMPiSm/z5AZK3t4zjOpJQ6BPECfiKAcqRUzkFmASQEhHzJOUgQ8BWyviwFsL4sBnC+LAE84YMWQnSAVCixdkvMAiB6Q7TCfJtrLq4PHkmSnHHbi0LHvOYa6w/g3kitjSgOYFyUUoWvlCPA9C1gvQfgDmiHNLZBgO8A3geZt+G6chQBA7hi/0QVQBrZ9EwQ0LbtbhgGghQAVFPAB25HmRH8b2/nAAAAAElFTkSuQmCC';

      HoverTool.prototype.initialize = function(attrs, options) {
        var r, renderers, tooltip, ttmodels, _i, _len, _ref2;
        HoverTool.__super__.initialize.call(this, attrs, options);
        ttmodels = {};
        renderers = this.get('plot').get('renderers');
        _ref2 = this.get('renderers');
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
          r = _ref2[_i];
          tooltip = new Tooltip.Model();
          ttmodels[r.id] = tooltip;
          renderers.push(tooltip);
        }
        this.set('ttmodels', ttmodels);
        this.get('plot').set('renderers', renderers);
      };

      HoverTool.prototype.defaults = function() {
        return _.extend({}, HoverTool.__super__.defaults.call(this), {
          snap_to_data: true,
          tooltips: [["index", "$index"], ["data (x, y)", "($x, $y)"], ["canvas (x, y)", "($sx, $sy)"]]
        });
      };

      return HoverTool;

    })(InspectTool.Model);
    HoverTools = (function(_super) {
      __extends(HoverTools, _super);

      function HoverTools() {
        _ref2 = HoverTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      HoverTools.prototype.model = HoverTool;

      return HoverTools;

    })(Collection);
    return {
      "Model": HoverTool,
      "Collection": new HoverTools(),
      "View": HoverToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=hover_tool.js.map
*/