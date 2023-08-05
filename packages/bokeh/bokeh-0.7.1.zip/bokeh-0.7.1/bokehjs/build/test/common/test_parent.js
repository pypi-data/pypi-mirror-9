(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "common/collection", "common/has_parent"], function(_, Collection, HasParent) {
    var TestParent, TestParents, _ref, _ref1;
    TestParent = (function(_super) {
      __extends(TestParent, _super);

      function TestParent() {
        _ref = TestParent.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      TestParent.prototype.type = 'TestParent';

      TestParent.prototype.parent_properties = ['testprop'];

      TestParent.prototype.display_defaults = function() {
        return _.extend({}, TestParent.__super__.display_defaults.call(this), {
          testprop: 'defaulttestprop'
        });
      };

      return TestParent;

    })(HasParent);
    TestParents = (function(_super) {
      __extends(TestParents, _super);

      function TestParents() {
        _ref1 = TestParents.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      TestParents.prototype.model = TestParent;

      return TestParents;

    })(Collection);
    return {
      "Model": TestParent,
      "Collection": new TestParents()
    };
  });

}).call(this);

/*
//@ sourceMappingURL=test_parent.js.map
*/