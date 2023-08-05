(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "backbone", "./tool", "./event_generators"], function(_, Backbone, Tool, EventGenerators) {
    var OnePointWheelEventGenerator, WheelZoomTool, WheelZoomToolView, WheelZoomTools, _ref, _ref1, _ref2;
    OnePointWheelEventGenerator = EventGenerators.OnePointWheelEventGenerator;
    WheelZoomToolView = (function(_super) {
      __extends(WheelZoomToolView, _super);

      function WheelZoomToolView() {
        _ref = WheelZoomToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      WheelZoomToolView.prototype.initialize = function(options) {
        var dims;
        WheelZoomToolView.__super__.initialize.call(this, options);
        dims = this.mget('dimensions');
        if (dims.length === 0) {
          return console.log("WARN: wheel zoom tool given empty dimensions");
        } else if (dims.length === 1) {
          if (dims[0] === 'width') {
            return this.evgen_options.buttonText = "Wheel Zoom (x-axis)";
          } else if (dims[0] === 'height') {
            return this.evgen_options.buttonText = "Wheel Zoom (y-axis)";
          } else {
            return console.log("WARN: wheel tool given unrecognized dimensions: " + dims);
          }
        } else if (dims.length === 2) {
          if (dims.indexOf('width') < 0 || dims.indexOf('height') < 0) {
            return console.log("WARN: pan tool given unrecognized dimensions: " + dims);
          }
        } else {
          return console.log("WARN: wheel tool given more than two dimensions: " + dims);
        }
      };

      WheelZoomToolView.prototype.eventGeneratorClass = OnePointWheelEventGenerator;

      WheelZoomToolView.prototype.evgen_options = {
        buttonText: "Wheel Zoom",
        buttonIcon: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAHFSURBVEiJ7ZbRceIwEIb/vbkCUgIl0EFcAlfBuYOkBHfApALTQUgF0AF0AFcBdPDlwStnsSXD3MA93OSf0ciWdveTrJVkA2RmeqSA/vnHQ0kZfQPvr7igoa0K5enGOBXwzqVOQAvMRkDgCVi60VDvF05j2DLjMwTPe6DDdt5Rx1kBi9A3z8DqEHiX/IEZ0IQJnIBZArYxoDts0qzC+yEDPAXY6PMD82DTJiBAHYLvhkF8xADVYN2SRrMPdk0yill69Hoh6Sxp6/WrJJlZ6o+Be7iZ7UtAjyVJ+jnsMbOVpNWEc/xsx5JRSaN9CLwOMmw54b8PfvWE3Us/wLCGVXBu+0W+HAxAM2jbhCysNNBgAk0W6IZNxjkHjFkI3Z5tvOxCe5eAJWBOOWCAHihrg2f7KGn+Rma2B94kpfXeer2X9GFm6f0+QNdvr9dm9qtkdJfbgu5ESvvzY8o2AidvBb6OrdwGr70+S1pfG508gzZX7NLxlDsvU8K0Od8cMJ2JbSFg2ktNpm8esnFxE9Drhe+ndGk2dPfcoQRzv9b7T1dhCllqZmtgq+7wfvZylvSmLvOOhRh/3G51C9DI/GI8Uv//X9s/B34CxIm8SDsIdkgAAAAASUVORK5CYII="
      };

      WheelZoomToolView.prototype.tool_events = {
        zoom: "_zoom"
      };

      WheelZoomToolView.prototype.mouse_coords = function(e, x, y) {
        var x_, y_, _ref1;
        _ref1 = [this.plot_view.canvas.sx_to_vx(x), this.plot_view.canvas.sy_to_vy(y)], x_ = _ref1[0], y_ = _ref1[1];
        return [x_, y_];
      };

      WheelZoomToolView.prototype._zoom = function(e) {
        var delta, dims, factor, multiplier, speed, sx_high, sx_low, sy_high, sy_low, x, xend, xr, xstart, y, yend, yr, ystart, zoom_info, _ref1, _ref2, _ref3, _ref4, _ref5;
        if (navigator.userAgent.toLowerCase().indexOf("firefox") > -1) {
          multiplier = 20;
        } else {
          multiplier = 1;
        }
        if (e.originalEvent.deltaY != null) {
          delta = -e.originalEvent.deltaY * multiplier;
        } else {
          delta = e.delta;
        }
        _ref1 = this.mouse_coords(e, e.bokehX, e.bokehY), x = _ref1[0], y = _ref1[1];
        speed = this.mget('speed');
        factor = speed * delta;
        if (factor > 0.9) {
          factor = 0.9;
        } else if (factor < -0.9) {
          factor = -0.9;
        }
        xr = this.plot_view.frame.get('h_range');
        sx_low = xr.get('start');
        sx_high = xr.get('end');
        yr = this.plot_view.frame.get('v_range');
        sy_low = yr.get('start');
        sy_high = yr.get('end');
        dims = this.mget('dimensions');
        if (dims.indexOf('width') > -1) {
          _ref2 = this.plot_view.xmapper.v_map_from_target([sx_low - (sx_low - x) * factor, sx_high - (sx_high - x) * factor]), xstart = _ref2[0], xend = _ref2[1];
        } else {
          _ref3 = this.plot_view.xmapper.v_map_from_target([sx_low, sx_high]), xstart = _ref3[0], xend = _ref3[1];
        }
        if (dims.indexOf('height') > -1) {
          _ref4 = this.plot_view.ymapper.v_map_from_target([sy_low - (sy_low - y) * factor, sy_high - (sy_high - y) * factor]), ystart = _ref4[0], yend = _ref4[1];
        } else {
          _ref5 = this.plot_view.ymapper.v_map_from_target([sy_low, sy_high]), ystart = _ref5[0], yend = _ref5[1];
        }
        zoom_info = {
          xr: {
            start: xstart,
            end: xend
          },
          yr: {
            start: ystart,
            end: yend
          },
          factor: factor
        };
        this.plot_view.update_range(zoom_info);
        return null;
      };

      return WheelZoomToolView;

    })(Tool.View);
    WheelZoomTool = (function(_super) {
      __extends(WheelZoomTool, _super);

      function WheelZoomTool() {
        _ref1 = WheelZoomTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      WheelZoomTool.prototype.default_view = WheelZoomToolView;

      WheelZoomTool.prototype.type = "WheelZoomTool";

      WheelZoomTool.prototype.defaults = function() {
        return {
          dimensions: ["width", "height"],
          speed: 1 / 600
        };
      };

      return WheelZoomTool;

    })(Tool.Model);
    WheelZoomTools = (function(_super) {
      __extends(WheelZoomTools, _super);

      function WheelZoomTools() {
        _ref2 = WheelZoomTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      WheelZoomTools.prototype.model = WheelZoomTool;

      WheelZoomTools.prototype.display_defaults = function() {
        return WheelZoomTools.__super__.display_defaults.call(this);
      };

      return WheelZoomTools;

    })(Backbone.Collection);
    return {
      "Model": WheelZoomTool,
      "Collection": new WheelZoomTools(),
      "View": WheelZoomToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=wheel_zoom_tool.js.map
*/