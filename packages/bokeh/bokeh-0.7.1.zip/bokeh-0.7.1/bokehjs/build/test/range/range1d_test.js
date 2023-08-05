(function() {
  require(["common/base", "range/range1d"], function(base, Range1d) {
    test('range1d_default_values', function() {
      var r;
      r = new Range1d.Model();
      equal(r.get('start'), 0);
      return equal(r.get('end'), 1);
    });
    test('range1d_setting', function() {
      var r;
      r = new Range1d.Model();
      r.set('start', 2);
      equal(r.get('start'), 2);
      r.set('end', 3);
      return equal(r.get('end'), 3);
    });
    return test('range1d_minmax', function() {
      var r;
      r = new Range1d.Model();
      equal(r.get('min'), 0);
      equal(r.get('max'), 1);
      r.set('start', 2);
      equal(r.get('min'), 1);
      equal(r.get('max'), 2);
      r.set('end', 3);
      equal(r.get('min'), 2);
      equal(r.get('max'), 3);
      r.set('end', -1.1);
      equal(r.get('min'), -1.1);
      return equal(r.get('max'), 2);
    });
  });

}).call(this);

/*
//@ sourceMappingURL=range1d_test.js.map
*/