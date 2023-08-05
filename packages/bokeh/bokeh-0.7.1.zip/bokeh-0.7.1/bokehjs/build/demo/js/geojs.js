(function() {
  var Collections, make_geojs_plot, opts, plot;

  Collections = Bokeh.Collections;

  make_geojs_plot = function(defaults, glyphspecs, _arg) {
    var axes, below, dims, left, legend, legend_name, pantool, plot, plot_title, reference_point, resettool, tools, wheelzoomtool, xaxis, xdr, yaxis, ydr;
    dims = _arg.dims, tools = _arg.tools, axes = _arg.axes, legend = _arg.legend, legend_name = _arg.legend_name, plot_title = _arg.plot_title, reference_point = _arg.reference_point;
    if (dims == null) {
      dims = [400, 400];
    }
    if (tools == null) {
      tools = true;
    }
    if (axes == null) {
      axes = true;
    }
    if (legend == null) {
      legend = true;
    }
    if (legend_name == null) {
      legend_name = "glyph";
    }
    if (plot_title == null) {
      plot_title = "";
    }
    xdr = Collections('Range1d').create();
    ydr = Collections('Range1d').create();
    plot = Collections('GeoJSPlot').create({
      map_options: {
        lat: 30.267153,
        lng: -97.74306079999997,
        zoom: 15
      },
      x_range: xdr,
      y_range: ydr,
      plot_width: dims[0],
      plot_height: dims[1],
      title: plot_title
    });
    plot.set(defaults);
    xaxis = Collections('LinearAxis').create({
      axis_label: 'x',
      plot: plot
    });
    below = plot.get('below');
    below.push(xaxis);
    plot.set('below', below);
    yaxis = Collections('LinearAxis').create({
      axis_label: 'y',
      plot: plot
    });
    left = plot.get('left');
    left.push(yaxis);
    plot.set('left', left);
    plot.add_renderers([xaxis, yaxis]);
    pantool = Collections('PanTool').create({
      dimensions: ['width', 'height']
    });
    wheelzoomtool = Collections('WheelZoomTool').create({
      dimensions: ['width', 'height']
    });
    resettool = Collections('ResetTool').create();
    plot.set_obj('tools', [pantool, wheelzoomtool, resettool]);
    return plot;
  };

  opts = {
    dims: [800, 800],
    tools: true,
    axes: true,
    legend: false,
    plot_title: "GeoJS Plot"
  };

  plot = make_geojs_plot({}, [], opts);

  Bokeh.Plotting.show(plot);

}).call(this);

/*
//@ sourceMappingURL=geojs.js.map
*/