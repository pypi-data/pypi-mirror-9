(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["common/has_parent", "common/continuum_view", "common/build_views", "backbone"], function(HasParent, continuum_view, build_views, Backbone) {
    var ContinuumView, VBoxModelForm, VBoxModelFormView, VBoxModelFormes, vboxmodelformes, _ref, _ref1, _ref2;
    ContinuumView = continuum_view.View;
    VBoxModelFormView = (function(_super) {
      __extends(VBoxModelFormView, _super);

      function VBoxModelFormView() {
        _ref = VBoxModelFormView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      VBoxModelFormView.prototype.tagName = "form";

      VBoxModelFormView.prototype.attributes = {
        "class": "bk-widget-form",
        role: "form"
      };

      VBoxModelFormView.prototype.initialize = function(options) {
        VBoxModelFormView.__super__.initialize.call(this, options);
        this.views = {};
        this.render();
        this.listenTo(this.model, 'change:children', this.change_children);
        return this.bind_children();
      };

      VBoxModelFormView.prototype.change_children = function() {
        var model, old_child_spec, old_children, _i, _len;
        old_children = this.model.previous('children');
        for (_i = 0, _len = old_children.length; _i < _len; _i++) {
          old_child_spec = old_children[_i];
          model = this.resolve_ref(old_child_spec);
          if (model) {
            this.stopListening(model, 'change:value');
          }
        }
        return this.bind_children();
      };

      VBoxModelFormView.prototype.bind_children = function() {
        var child, children, _i, _len, _results;
        children = this.mget('_children');
        _results = [];
        for (_i = 0, _len = children.length; _i < _len; _i++) {
          child = children[_i];
          _results.push(this.listenTo(child, {
            'change:value': this.set_data
          }));
        }
        return _results;
      };

      VBoxModelFormView.prototype.set_data = function(model, value, options) {
        var name, _i, _len, _ref1, _ref2, _ref3;
        if (model != null) {
          _ref1 = [model.get('name'), model.get('value')], name = _ref1[0], value = _ref1[1];
          value = this.model.convert_val(name, value);
          this.mset(name, value);
          return this.model.save();
        } else {
          _ref2 = this.mget('children');
          for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
            model = _ref2[_i];
            _ref3 = [model.get('name'), model.get('value')], name = _ref3[0], value = _ref3[1];
            if ((name != null) && (value != null)) {
              value = this.model.convert_val(name, value);
              this.mset(name, value);
            }
          }
          return this.model.save();
        }
      };

      VBoxModelFormView.prototype.render = function() {
        var child, children, key, val, _i, _len, _ref1, _results;
        children = this.mget('_children');
        build_views(this.views, children);
        _ref1 = this.views;
        for (key in _ref1) {
          if (!__hasProp.call(_ref1, key)) continue;
          val = _ref1[key];
          val.$el.detach();
        }
        this.$el.empty();
        _results = [];
        for (_i = 0, _len = children.length; _i < _len; _i++) {
          child = children[_i];
          this.$el.append("<br/");
          _results.push(this.$el.append(this.views[child.id].$el));
        }
        return _results;
      };

      return VBoxModelFormView;

    })(ContinuumView);
    VBoxModelForm = (function(_super) {
      __extends(VBoxModelForm, _super);

      function VBoxModelForm() {
        _ref1 = VBoxModelForm.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      VBoxModelForm.prototype.type = "VBoxModelForm";

      VBoxModelForm.prototype.default_view = VBoxModelFormView;

      VBoxModelForm.prototype.convert_val = function(name, value) {
        var field_defs;
        field_defs = this.get('_field_defs');
        if (field_defs[name] != null) {
          if (field_defs[name] === "Float") {
            value = parseFloat(value);
          } else if (field_defs[name] === "Int") {
            value = parseInt(value);
          }
        }
        return value;
      };

      VBoxModelForm.prototype.defaults = function() {
        var defaults;
        defaults = {
          _children: [],
          _field_defs: {}
        };
        return defaults;
      };

      return VBoxModelForm;

    })(HasParent);
    VBoxModelFormes = (function(_super) {
      __extends(VBoxModelFormes, _super);

      function VBoxModelFormes() {
        _ref2 = VBoxModelFormes.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      VBoxModelFormes.prototype.model = VBoxModelForm;

      return VBoxModelFormes;

    })(Backbone.Collection);
    vboxmodelformes = new VBoxModelFormes();
    return {
      "Model": VBoxModelForm,
      "Collection": vboxmodelformes,
      "View": VBoxModelFormView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=vboxmodelform.js.map
*/