(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["common/collection", "common/has_properties"], function(Collection, HasProperties) {
    var TestObject, TestObjects, _ref, _ref1;
    TestObject = (function(_super) {
      __extends(TestObject, _super);

      function TestObject() {
        _ref = TestObject.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      TestObject.prototype.type = 'TestObject';

      return TestObject;

    })(HasProperties);
    TestObjects = (function(_super) {
      __extends(TestObjects, _super);

      function TestObjects() {
        _ref1 = TestObjects.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      TestObjects.prototype.model = TestObject;

      TestObjects.prototype.url = "/";

      return TestObjects;

    })(Collection);
    return {
      "Model": TestObject,
      "Collection": new TestObjects()
    };
  });

}).call(this);

/*
//@ sourceMappingURL=test_object.js.map
*/