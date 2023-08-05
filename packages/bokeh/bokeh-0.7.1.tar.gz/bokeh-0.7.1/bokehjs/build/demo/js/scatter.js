(function() {
  require(['main'], function(Bokeh) {
    var data, i, options, plot, r, scatter, val, x, y;
    r = new Bokeh.Random(123456789);
    x = (function() {
      var _i, _len, _ref, _results;
      _ref = _.range(4000);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        _results.push(r.randf() * 100);
      }
      return _results;
    })();
    y = (function() {
      var _i, _len, _ref, _results;
      _ref = _.range(4000);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        _results.push(r.randf() * 100);
      }
      return _results;
    })();
    data = {
      x: x,
      y: y,
      radius: (function() {
        var _i, _len, _ref, _results;
        _ref = _.range(4000);
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          i = _ref[_i];
          _results.push(r.randf() + 0.3);
        }
        return _results;
      })(),
      color: (function() {
        var _i, _len, _ref, _results;
        _ref = _.zip(x, y);
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          val = _ref[_i];
          _results.push("rgb(" + (Math.floor(50 + 2 * val[0])) + ", " + (Math.floor(30 + 2 * val[1])) + ", 150)");
        }
        return _results;
      })()
    };
    scatter = {
      type: 'circle',
      x: 'x',
      y: 'y',
      radius: 'radius',
      radius_units: 'data',
      fill_color: 'color',
      fill_alpha: 0.6,
      line_color: null
    };
    options = {
      title: "Scatter Demo",
      nonselected: {
        fill_color: 'black',
        line_alpha: 0.1,
        fill_alpha: 0.05
      },
      dims: [600, 600],
      xrange: [0, 100],
      yrange: [0, 100],
      xaxes: "below",
      yaxes: "left",
      tools: true,
      legend: false
    };
    plot = Bokeh.Plotting.make_plot(scatter, data, options);
    return Bokeh.Plotting.show(plot);
  });

}).call(this);

/*
//@ sourceMappingURL=scatter.js.map
*/