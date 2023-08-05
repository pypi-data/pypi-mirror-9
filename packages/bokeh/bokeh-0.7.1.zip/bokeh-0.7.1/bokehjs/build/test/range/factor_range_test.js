(function() {
  require(["common/base", "range/factor_range"], function(base, FactorRange) {
    test('factor_range_default_values', function() {
      var r;
      r = new FactorRange.Model();
      return deepEqual(r.get('factors'), []);
    });
    test('factor_range_setting', function() {
      var r;
      r = new FactorRange.Model();
      r.set('factors', ['FOO']);
      return deepEqual(r.get('factors'), ['FOO']);
    });
    return test('factor_range_minmax', function() {
      var r;
      r = new FactorRange.Model();
      r.set('factors', ['FOO']);
      equal(r.get('min'), 0.5);
      equal(r.get('max'), 1.5);
      r.set('factors', ['FOO', 'BAR']);
      equal(r.get('min'), 0.5);
      equal(r.get('max'), 2.5);
      r.set('factors', ['A', 'B', 'C']);
      equal(r.get('min'), 0.5);
      return equal(r.get('max'), 3.5);
    });
  });

}).call(this);

/*
//@ sourceMappingURL=factor_range_test.js.map
*/