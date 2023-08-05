(function() {
  require(["underscore", "common/base", "common/continuum_view", "common/has_properties", "../test/common/test_object"], function(_, base, ContinuumView, HasProperties, test_object) {
    var testobjects;
    testobjects = test_object.Collection;
    base.locations['TestObject'] = "../test/common/test_object";
    base.mod_cache["../test/common/test_object"] = test_object;
    test('computed_properties', function() {
      var model, temp;
      testobjects.reset();
      model = testobjects.create({
        'a': 1,
        'b': 1
      });
      model.register_property('c', function() {
        return this.get('a') + this.get('b');
      });
      model.add_dependencies('c', model, ['a', 'b']);
      temp = model.get('c');
      return ok(temp === 2);
    });
    test('cached_properties_react_changes', function() {
      var model, temp;
      testobjects.reset();
      model = testobjects.create({
        'a': 1,
        'b': 1
      });
      model.register_property('c', function() {
        return this.get('a') + this.get('b');
      }, true);
      model.add_dependencies('c', model, ['a', 'b']);
      temp = model.get('c');
      ok(temp === 2);
      temp = model.get_cache('c');
      ok(!_.isUndefined(temp));
      model.set('a', 10);
      temp = model.get_cache('c');
      temp = model.get('c');
      return ok(temp === 11);
    });
    test('has_prop_manages_event_lifcycle', function() {
      var model, model2, triggered;
      testobjects.reset();
      model = testobjects.create({
        'a': 1,
        'b': 1
      });
      model2 = testobjects.create({
        'a': 1,
        'b': 1
      });
      triggered = false;
      model.listenTo(model2, 'change', function() {
        return triggered = true;
      });
      model2.set({
        'a': 2
      });
      ok(triggered);
      triggered = false;
      model.destroy();
      model2.set({
        'a': 3
      });
      return ok(!triggered);
    });
    test('has_prop_manages_event_for_views', function() {
      var model, model2, triggered, view;
      testobjects.reset();
      model = testobjects.create({
        'a': 1,
        'b': 1
      });
      model2 = testobjects.create({
        'a': 1,
        'b': 1
      });
      view = new ContinuumView({
        'model': model2
      });
      triggered = false;
      view.listenTo(model, 'change', function() {
        return triggered = true;
      });
      model.set({
        'a': 2
      });
      ok(triggered);
      triggered = false;
      view.remove();
      model.set({
        'a': 3
      });
      return ok(!triggered);
    });
    test('property_setters', function() {
      var model, prop, setter;
      testobjects.reset();
      model = testobjects.create({
        'a': 1,
        'b': 1
      });
      prop = function() {
        return this.get('a') + this.get('b');
      };
      setter = function(val) {
        this.set('a', val / 2, {
          silent: true
        });
        return this.set('b', val / 2);
      };
      model.register_property('c', prop, true);
      model.add_dependencies('c', model, ['a', 'b']);
      model.register_setter('c', setter);
      model.set('c', 100);
      ok(model.get('a') === 50);
      return ok(model.get('b') === 50);
    });
    return test('test_vectorized_ref', function() {
      var model1, model2, model3, model4, output;
      testobjects.reset();
      model1 = testobjects.create({
        a: 1,
        b: 1
      });
      model2 = testobjects.create({
        a: 2,
        b: 2
      });
      model3 = testobjects.create({
        a: 1,
        b: 1,
        vectordata: [model1.ref(), model2.ref()]
      });
      model4 = testobjects.create({
        a: 1,
        b: 1,
        vectordata: [[model1.ref(), model2.ref()]]
      });
      output = model3.get('vectordata');
      ok(output[0] === model1);
      ok(output[1] === model2);
      model3.set_obj('vectordata2', [model1, model1, model2]);
      output = model3.get('vectordata2', false);
      ok(output[0].id === model1.ref().id);
      ok(output[1].id === model1.ref().id);
      ok(output[2].id === model2.ref().id);
      ok(!(output[0] instanceof HasProperties));
      output = model4.get('vectordata');
      ok(output[0][0] === model1);
      return ok(output[0][1] === model2);
    });
  });

}).call(this);

/*
//@ sourceMappingURL=has_property_test.js.map
*/