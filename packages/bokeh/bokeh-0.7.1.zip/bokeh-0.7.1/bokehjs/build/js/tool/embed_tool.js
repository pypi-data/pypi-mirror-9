(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "jquery", "bootstrap/modal", "backbone", "./tool", "./event_generators", "./embed_tool_template"], function(_, $, $$1, Backbone, Tool, EventGenerators, embed_tool_template) {
    var ButtonEventGenerator, EmbedTool, EmbedToolView, EmbedTools, escapeHTML, _ref, _ref1, _ref2;
    ButtonEventGenerator = EventGenerators.ButtonEventGenerator;
    escapeHTML = function(unsafe_str) {
      return unsafe_str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\"/g, '&quot;').replace(/\'/g, '&#39;');
    };
    EmbedToolView = (function(_super) {
      __extends(EmbedToolView, _super);

      function EmbedToolView() {
        _ref = EmbedToolView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      EmbedToolView.prototype.initialize = function(options) {
        return EmbedToolView.__super__.initialize.call(this, options);
      };

      EmbedToolView.prototype.eventGeneratorClass = ButtonEventGenerator;

      EmbedToolView.prototype.evgen_options = {
        buttonText: "Embed Html"
      };

      EmbedToolView.prototype.toolType = "EmbedTool";

      EmbedToolView.prototype.tool_events = {
        activated: "_activated",
        deactivated: "_close_modal"
      };

      EmbedToolView.prototype._activated = function(e) {
        var baseurl, doc_apikey, doc_id, model_id, script_inject_escaped,
          _this = this;
        console.log("EmbedToolView._activated");
        window.tool_view = this;
        model_id = this.plot_model.get('id');
        doc_id = this.plot_model.get('doc');
        doc_apikey = this.plot_model.get('docapikey');
        baseurl = this.plot_model.get('baseurl');
        script_inject_escaped = escapeHTML(this.plot_model.get('script_inject_snippet'));
        this.$modal = $(embed_tool_template({
          script_inject_escaped: script_inject_escaped
        }));
        $('body').append(this.$modal);
        this.$modal.on('hidden', function() {
          return _this.plot_view.eventSink.trigger("clear_active_tool");
        });
        return this.$modal.modal({
          show: true
        });
      };

      EmbedToolView.prototype._close_modal = function() {
        return this.$modal.remove();
      };

      return EmbedToolView;

    })(Tool.View);
    EmbedTool = (function(_super) {
      __extends(EmbedTool, _super);

      function EmbedTool() {
        _ref1 = EmbedTool.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      EmbedTool.prototype.default_view = EmbedToolView;

      EmbedTool.prototype.type = "EmbedTool";

      return EmbedTool;

    })(Tool.Model);
    EmbedTools = (function(_super) {
      __extends(EmbedTools, _super);

      function EmbedTools() {
        _ref2 = EmbedTools.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      EmbedTools.prototype.model = EmbedTool;

      EmbedTools.prototype.display_defaults = function() {
        return EmbedTools.__super__.display_defaults.call(this);
      };

      return EmbedTools;

    })(Backbone.Collection);
    return {
      Model: EmbedTool,
      Collection: new EmbedTools(),
      View: EmbedToolView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=embed_tool.js.map
*/