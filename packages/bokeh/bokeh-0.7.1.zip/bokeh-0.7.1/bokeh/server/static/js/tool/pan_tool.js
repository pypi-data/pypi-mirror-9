(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "backbone", "./tool", "./event_generators"], function(_, Backbone, Tool, EventGenerators) {
    var PanTool, PanToolView, PanTools, TwoPointEventGenerator, _ref, _ref1, _ref2;
    TwoPointEventGenerator = EventGenerators.TwoPointEventGenerator;
    window.render_count = 0;
    PanToolView = (function(_super) {
      __extends(PanToolView, _super);

      function PanToolView() {
        _ref = PanToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      PanToolView.prototype.initialize = function(options) {
        var dims;
        PanToolView.__super__.initialize.call(this, options);
        dims = this.mget('dimensions');
        if (dims.length === 0) {
          return console.log("WARN: pan tool given empty dimensions");
        } else if (dims.length === 1) {
          if (dims[0] === 'width') {
            return this.evgen_options.buttonText = "Pan (x-axis)";
          } else if (dims[0] === 'height') {
            return this.evgen_options.buttonText = "Pan (y-axis)";
          } else {
            return console.log("WARN: pan tool given unrecognized dimensions: " + dims);
          }
        } else if (dims.length === 2) {
          if (dims.indexOf('width') < 0 || dims.indexOf('height') < 0) {
            return console.log("WARN: pan tool given unrecognized dimensions: " + dims);
          }
        } else {
          return console.log("WARN: pan tool given more than two dimensions: " + dims);
        }
      };

      PanToolView.prototype.bind_bokeh_events = function() {
        return PanToolView.__super__.bind_bokeh_events.call(this);
      };

      PanToolView.prototype.eventGeneratorClass = TwoPointEventGenerator;

      PanToolView.prototype.toolType = "PanTool";

      PanToolView.prototype.evgen_options = {
        keyName: null,
        buttonText: "Pan",
        buttonIcon: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAEwSURBVEiJ5ZbtUcMwDIZfcR0gGxAmICNkhI5QJiEb9DpB2QA2KBskG8AGZYOHH3XAl+bDjpMed7y/fD5Jj2VJTgToFgIE6G6mc55EjrTPgA9gH8sB4oAOVvOr3drAI9cqVwEC+x4YwDmkprMydI5lS4r0m9+lKfqnQGCbEhTIB2P4tffm7DQSbLJpPJvK5wDaeBuFpJOkTFIzMl+FH3jC5hl4lPQk6csnbwdmbCnV3bF4l/Q2dEUL6PCz6tSwcidaqoZnV6r+wTezSv59p6mR9GBmTfc0fSfMhqIEZnjl35thKzNLynDM/2+8NGtqM21yEZevey7p3tur3PLFzD5DA4XaFa7Nu3oN5TDjF6PswOqxjk4GOsedN9RBsCSgc67aFyQWaIDMLBoaC2t187H4BqwdDXMWZF/nAAAAAElFTkSuQmCC",
        cursor: "move",
        auto_deactivate: true,
        restrict_to_innercanvas: true
      };

      PanToolView.prototype.tool_events = {
        UpdatingMouseMove: "_drag",
        SetBasepoint: "_set_base_point"
      };

      PanToolView.prototype.mouse_coords = function(e, x, y) {
        var x_, y_, _ref1;
        _ref1 = [this.plot_view.canvas.sx_to_vx(x), this.plot_view.canvas.sy_to_vy(y)], x_ = _ref1[0], y_ = _ref1[1];
        return [x_, y_];
      };

      PanToolView.prototype._set_base_point = function(e) {
        var _ref1;
        _ref1 = this.mouse_coords(e, e.bokehX, e.bokehY), this.x = _ref1[0], this.y = _ref1[1];
        return null;
      };

      PanToolView.prototype._drag = function(e) {
        var dims, pan_info, sdx, sdy, sx_high, sx_low, sy_high, sy_low, x, xdiff, xend, xr, xstart, y, ydiff, yend, yr, ystart, _ref1, _ref2;
        _ref1 = this.mouse_coords(e, e.bokehX, e.bokehY), x = _ref1[0], y = _ref1[1];
        xdiff = x - this.x;
        ydiff = y - this.y;
        _ref2 = [x, y], this.x = _ref2[0], this.y = _ref2[1];
        xr = this.plot_view.frame.get('h_range');
        sx_low = xr.get('start') - xdiff;
        sx_high = xr.get('end') - xdiff;
        yr = this.plot_view.frame.get('v_range');
        sy_low = yr.get('start') - ydiff;
        sy_high = yr.get('end') - ydiff;
        dims = this.mget('dimensions');
        if (dims.indexOf('width') > -1) {
          xstart = this.plot_view.xmapper.map_from_target(sx_low);
          xend = this.plot_view.xmapper.map_from_target(sx_high);
          sdx = -xdiff;
        } else {
          xstart = this.plot_view.xmapper.map_from_target(xr.get('start'));
          xend = this.plot_view.xmapper.map_from_target(xr.get('end'));
          sdx = 0;
        }
        if (dims.indexOf('height') > -1) {
          ystart = this.plot_view.ymapper.map_from_target(sy_low);
          yend = this.plot_view.ymapper.map_from_target(sy_high);
          sdy = ydiff;
        } else {
          ystart = this.plot_view.ymapper.map_from_target(yr.get('start'));
          yend = this.plot_view.ymapper.map_from_target(yr.get('end'));
          sdy = 0;
        }
        pan_info = {
          xr: {
            start: xstart,
            end: xend
          },
          yr: {
            start: ystart,
            end: yend
          },
          sdx: sdx,
          sdy: sdy
        };
        this.plot_view.update_range(pan_info);
        return null;
      };

      return PanToolView;

    })(Tool.View);
    PanTool = (function(_super) {
      __extends(PanTool, _super);

      function PanTool() {
        _ref1 = PanTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      PanTool.prototype.default_view = PanToolView;

      PanTool.prototype.type = "PanTool";

      PanTool.prototype.defaults = function() {
        return {
          dimensions: ["width", "height"]
        };
      };

      PanTool.prototype.display_defaults = function() {
        return PanTool.__super__.display_defaults.call(this);
      };

      return PanTool;

    })(Tool.Model);
    PanTools = (function(_super) {
      __extends(PanTools, _super);

      function PanTools() {
        _ref2 = PanTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      PanTools.prototype.model = PanTool;

      return PanTools;

    })(Backbone.Collection);
    return {
      "Model": PanTool,
      "Collection": new PanTools(),
      "View": PanToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=pan_tool.js.map
*/