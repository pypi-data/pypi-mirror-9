(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "backbone", "./tool", "./event_generators"], function(_, Backbone, Tool, EventGenerators) {
    var ButtonEventGenerator, ResetTool, ResetToolView, ResetTools, _ref, _ref1, _ref2;
    ButtonEventGenerator = EventGenerators.ButtonEventGenerator;
    ResetToolView = (function(_super) {
      __extends(ResetToolView, _super);

      function ResetToolView() {
        _ref = ResetToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      ResetToolView.prototype.initialize = function(options) {
        return ResetToolView.__super__.initialize.call(this, options);
      };

      ResetToolView.prototype.eventGeneratorClass = ButtonEventGenerator;

      ResetToolView.prototype.evgen_options = {
        buttonText: "Reset View",
        buttonIcon: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAABx0RVh0U29mdHdhcmUAQWRvYmUgRmlyZXdvcmtzIENTNui8sowAAAJASURBVEiJ3Za9axVBEMB/K3nRSBqLoEkhIY36ED8wgp02FsaPwsrSIiAYSOVLQCG9liqCqPgPSAqJWGhjkZhKNCZYKoIYsLIxHybvZ3EbuVzu7r2nUcGBKXZvZn47uzc7G1T+pmz5q7R/AWxLD0IIuUZqBegGTgKHgUPAMvAGeA+MA/MhhJWMX26wn1oA61cfqKsWy6p6X63mxO5MM0IalM1QHQauA9vi1IuY0Yc41wXsjpkDLAEjIYSb0f80cA641DBDdSyVwSP1lNpesAsD6kTK/ppaU1fUuXWMPKA6lHKuFYEy0A71as52T5YC1aq6HI2vNAJloIMp3zWZKgTW6/WgPoyG4+rWJkG96tPoVy8DrqvDEMJ+4CLJL38rhLDUZHLHgB3ACpBfW6nVpXWvOqM+N6m9lkQ9q95TF1s5w261r1VYBtyvjqjz6mwpcDNF7VGPFgLjx55NBG7Q7MSs+tmk9o78JqwaMywFTqYO+1v8Ac78AqyiTqtv1T1lwCk3ynf1pXqhBeCJuGDVA4V1mOdL0sK+AtNNwjqBUaADuAPMZA3KMlxWB5vNLMarRd8FdV/2DNuy9plxBehSO0IICw1A24Eh4Eacugy8yzNM65xJS6mZtJg1mVAHCkAVk9aVbk9jObE3NmDgLvA4hPAkOgzHFa9d4s+Aj8CXON4F9ALHSe7QRWA01YBzV5jWzpzvVRs/MerqbbW/JHbjJ0Z624CdwHmgDzgItAOvgVcx808hhNUsMCvZLf3j8v8/hH8At02YtB91tJYAAAAASUVORK5CYII="
      };

      ResetToolView.prototype.toolType = "ResetTool";

      ResetToolView.prototype.tool_events = {
        activated: "_activated"
      };

      ResetToolView.prototype._activated = function(e) {
        var _this = this;
        this.plot_view.update_range();
        return _.delay((function() {
          return _this.plot_view.eventSink.trigger("clear_active_tool");
        }), 100);
      };

      return ResetToolView;

    })(Tool.View);
    ResetTool = (function(_super) {
      __extends(ResetTool, _super);

      function ResetTool() {
        _ref1 = ResetTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      ResetTool.prototype.default_view = ResetToolView;

      ResetTool.prototype.type = "ResetTool";

      return ResetTool;

    })(Tool.Model);
    ResetTools = (function(_super) {
      __extends(ResetTools, _super);

      function ResetTools() {
        _ref2 = ResetTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      ResetTools.prototype.model = ResetTool;

      ResetTools.prototype.display_defaults = function() {
        return ResetTools.__super__.display_defaults.call(this);
      };

      return ResetTools;

    })(Backbone.Collection);
    return {
      "Model": ResetTool,
      "Collection": new ResetTools(),
      "View": ResetToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=reset_tool.js.map
*/