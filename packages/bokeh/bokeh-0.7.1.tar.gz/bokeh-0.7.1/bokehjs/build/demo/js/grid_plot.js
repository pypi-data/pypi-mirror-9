(function() {
  var gridplot, options, plot1, plot2, scatter1, scatter2, source, x, xdr, xs, ydr1, ydr2, ys1, ys2;

  xs = (function() {
    var _i, _len, _ref, _results;
    _ref = _.range(630);
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      x = _ref[_i];
      _results.push(x / 50);
    }
    return _results;
  })();

  ys1 = (function() {
    var _i, _len, _results;
    _results = [];
    for (_i = 0, _len = xs.length; _i < _len; _i++) {
      x = xs[_i];
      _results.push(Math.sin(x));
    }
    return _results;
  })();

  ys2 = (function() {
    var _i, _len, _results;
    _results = [];
    for (_i = 0, _len = xs.length; _i < _len; _i++) {
      x = xs[_i];
      _results.push(Math.cos(x));
    }
    return _results;
  })();

  source = Bokeh.Collections('ColumnDataSource').create({
    data: {
      x: xs,
      y1: ys1,
      y2: ys2
    }
  });

  xdr = Bokeh.Collections('DataRange1d').create({
    sources: [
      {
        source: source,
        columns: ['x']
      }
    ]
  });

  ydr1 = Bokeh.Collections('DataRange1d').create({
    sources: [
      {
        source: source,
        columns: ['y1']
      }
    ]
  });

  ydr2 = Bokeh.Collections('DataRange1d').create({
    sources: [
      {
        source: source,
        columns: ['y2']
      }
    ]
  });

  scatter1 = {
    type: 'circle',
    x: 'x',
    y: 'y1',
    radius: 8,
    radius_units: 'screen',
    fill_color: 'red',
    line_color: 'black'
  };

  scatter2 = {
    type: 'rect',
    x: 'x',
    y: 'y2',
    width: 5,
    width_units: 'screen',
    height: 5,
    height_units: 'screen',
    fill_color: 'blue'
  };

  options = {
    title: "Scatter Demo",
    dims: [600, 600],
    xrange: xdr,
    xaxes: "below",
    yaxes: "left",
    tools: true,
    legend: false
  };

  plot1 = Bokeh.Plotting.make_plot(scatter1, source, _.extend({
    title: "Plot 1",
    yrange: ydr1
  }, options));

  plot2 = Bokeh.Plotting.make_plot(scatter2, source, _.extend({
    title: "Plot 2",
    yrange: ydr2
  }, options));

  gridplot = Bokeh.Collections('GridPlot').create({
    children: [[plot1, plot2]]
  });

  Bokeh.Plotting.show(gridplot);

}).call(this);

/*
//@ sourceMappingURL=grid_plot.js.map
*/