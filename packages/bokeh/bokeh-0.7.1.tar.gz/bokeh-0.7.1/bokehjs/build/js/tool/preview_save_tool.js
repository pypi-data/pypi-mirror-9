(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "jquery", "bootstrap/modal", "backbone", "common/bulk_save", "./tool", "./event_generators", "./preview_save_tool_template"], function(_, $, $$1, Backbone, bulk_save, Tool, EventGenerators, preview_save_tool_template) {
    var ButtonEventGenerator, PreviewSaveTool, PreviewSaveToolView, PreviewSaveTools, _ref, _ref1, _ref2;
    ButtonEventGenerator = EventGenerators.ButtonEventGenerator;
    PreviewSaveToolView = (function(_super) {
      __extends(PreviewSaveToolView, _super);

      function PreviewSaveToolView() {
        _ref = PreviewSaveToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      PreviewSaveToolView.prototype.initialize = function(options) {
        return PreviewSaveToolView.__super__.initialize.call(this, options);
      };

      PreviewSaveToolView.prototype.eventGeneratorClass = ButtonEventGenerator;

      PreviewSaveToolView.prototype.evgen_options = {
        buttonText: "Preview/Save",
        buttonIcon: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAE4SURBVEiJ5ZbhTcMwEIW/h/hPN6AbUCagbNANKJNQJqiYgI7SbpARygRNJ3j8iFOq1E6s0BSpPClK4rPv+XzvbMs2l8TNRdn+gvA20jYCHvo4k7RJ2Q6ps918CvfHzvYsRWgbRURj4AtYAVPgKTL+AyjD94xqRTbABLgDXiWtciO07XWwLWJhNBzVfaa2J7bL8D+PRXhW0UgqqFZlD3w2SWEAlXaRDlIWDdKl7dGvCI8dUJVRinQR7AflxurwGGWifZe5JRbhPc4lXFFJfdzejULSOmcGrYSSSmCe4ygX/3PzPiCocUl3Dpt4T+W0SzRz+uVQVHV4gq4lrWvsWZnomsn1i+b6CVMqvbf9xs9p/2I7dvKnUI8fNw2xK0ZBz0tUCx6D31NCSdienpFsK2lb88QiHBQXF803MWL34Bj7qCQAAAAASUVORK5CYII="
      };

      PreviewSaveToolView.prototype.toolType = "PreviewSaveTool";

      PreviewSaveToolView.prototype.tool_events = {
        activated: "_activated",
        deactivated: "_close_modal"
      };

      PreviewSaveToolView.prototype._activated = function(e) {
        var data_uri,
          _this = this;
        data_uri = this.plot_view.canvas_view.canvas[0].toDataURL();
        this.plot_model.set('png', this.plot_view.canvas_view.canvas[0].toDataURL());
        this.$modal = $(preview_save_tool_template({
          data_uri: data_uri
        }));
        $('body').append(this.$modal);
        this.$modal.on('hidden', function() {
          return _this.plot_view.eventSink.trigger("clear_active_tool");
        });
        return this.$modal.modal({
          show: true
        });
      };

      PreviewSaveToolView.prototype._close_modal = function() {
        return this.$modal.remove();
      };

      return PreviewSaveToolView;

    })(Tool.View);
    PreviewSaveTool = (function(_super) {
      __extends(PreviewSaveTool, _super);

      function PreviewSaveTool() {
        _ref1 = PreviewSaveTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      PreviewSaveTool.prototype.default_view = PreviewSaveToolView;

      PreviewSaveTool.prototype.type = "PreviewSaveTool";

      PreviewSaveTool.prototype.display_defaults = function() {
        return PreviewSaveTool.__super__.display_defaults.call(this);
      };

      return PreviewSaveTool;

    })(Tool.Model);
    PreviewSaveTools = (function(_super) {
      __extends(PreviewSaveTools, _super);

      function PreviewSaveTools() {
        _ref2 = PreviewSaveTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      PreviewSaveTools.prototype.model = PreviewSaveTool;

      return PreviewSaveTools;

    })(Backbone.Collection);
    return {
      Model: PreviewSaveTool,
      Collection: new PreviewSaveTools(),
      View: PreviewSaveToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=preview_save_tool.js.map
*/