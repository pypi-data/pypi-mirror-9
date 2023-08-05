(function() {
  var Collections, FREQ_SAMPLES, FREQ_SLIDER_MAX, FREQ_SLIDER_MIN, FREQ_SLIDER_START, GAIN_DEFAULT, GAIN_MAX, GAIN_MIN, HIST_NUM_BINS, LinearColorMapper, MAX_FREQ, NGRAMS, NUM_SAMPLES, RadialHistogramPlot, SAMPLING_RATE, SPECTROGRAM_LENGTH, SimpleIndexPlot, SpectrogramApp, SpectrogramPlot, all_palettes, requestAnimationFrame;

  Collections = Bokeh.Collections;

  all_palettes = Bokeh.Palettes.all_palettes;

  LinearColorMapper = Bokeh.LinearColorMapper;

  NUM_SAMPLES = 1024;

  SAMPLING_RATE = 44100;

  MAX_FREQ = SAMPLING_RATE / 2;

  FREQ_SAMPLES = NUM_SAMPLES / 8;

  SPECTROGRAM_LENGTH = 512;

  window.TIMESLICE = 40;

  NGRAMS = 800;

  HIST_NUM_BINS = 16;

  FREQ_SLIDER_MAX = MAX_FREQ;

  FREQ_SLIDER_MIN = 0;

  FREQ_SLIDER_START = FREQ_SLIDER_MAX / 2;

  GAIN_DEFAULT = 1;

  GAIN_MIN = 1;

  GAIN_MAX = 20;

  requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;

  SpectrogramApp = (function() {
    function SpectrogramApp() {
      var _this = this;
      this.gain = GAIN_DEFAULT;
      this.paused = false;
      this.throttled_request_data = _.throttle((function() {
        return _this.request_data();
      }), 40);
      this.spec_plot = new SpectrogramPlot({
        width: NGRAMS,
        height: SPECTROGRAM_LENGTH / 2 + 80
      });
      this.power_plot = new SimpleIndexPlot({
        x0: 0,
        x1: window.TIMESLICE + 0.1,
        y0: -0.6,
        y1: 0.7,
        width: 800,
        height: 250
      });
      this.fft_plot = new SimpleIndexPlot({
        x0: FREQ_SLIDER_MIN,
        x1: FREQ_SLIDER_MAX,
        y0: -1,
        y1: 26,
        width: 800,
        height: 250
      });
      this.hist_plot = new RadialHistogramPlot({
        num_bins: HIST_NUM_BINS,
        width: 500,
        height: 500
      });
      this.render();
    }

    SpectrogramApp.prototype.request_data = function() {
      var _this = this;
      if (this.paused) {
        return;
      }
      return $.ajax('http://localhost:5000/data', {
        type: 'GET',
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) {},
        success: function(data, textStatus, jqXHR) {
          if (data[0] == null) {
            return _.delay((function() {
              return _this.throttled_request_data;
            }), 130);
          } else {
            _this.on_data(data);
            return requestAnimationFrame(function() {
              return _this.throttled_request_data();
            });
          }
        }
      });
    };

    SpectrogramApp.prototype.on_data = function(data) {
      var i, _i, _j, _ref, _ref1;
      for (i = _i = 0, _ref = data[0].length - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        data[0][i] *= this.gain;
      }
      for (i = _j = 0, _ref1 = data[1].length - 1; 0 <= _ref1 ? _j <= _ref1 : _j >= _ref1; i = 0 <= _ref1 ? ++_j : --_j) {
        data[1][i] *= this.gain;
      }
      this.spec_plot.update(data[0]);
      this.power_plot.update(data[1]);
      this.fft_plot.update(data[0]);
      this.hist_plot.update(data[0], this.fft_range[0], this.fft_range[1]);
      return this.hist_plot.update(data[0], 0, MAX_FREQ);
    };

    SpectrogramApp.prototype.set_freq_range = function(event, ui) {
      var max, min, _ref;
      _ref = this.fft_range = ui.values, min = _ref[0], max = _ref[1];
      this.spec_plot.set_yrange(min, max);
      return this.fft_plot.set_xrange(min, max);
    };

    SpectrogramApp.prototype.render = function() {
      var button, controls, div, label, myrender, slider, slider_div, sliders,
        _this = this;
      controls = $('<div></div>');
      button = $('<button id="pause">pause</button>');
      button.on("click", function() {
        if (button.text() === 'pause') {
          button.text('resume');
          return _this.paused = true;
        } else {
          button.text('pause');
          _this.paused = false;
          return _this.request_data();
        }
      });
      button.css('margin-top', '50px');
      controls.append(button);
      sliders = $('<div></div>');
      slider = $('<div></div>');
      label = $("<p>freq range:</p>");
      slider.append(label);
      slider_div = $('<div id="freq-range-slider" style="height: 160px;"></div>');
      slider_div.slider({
        orientation: "vertical",
        animate: "fast",
        step: 1,
        min: FREQ_SLIDER_MIN,
        max: FREQ_SLIDER_MAX,
        values: [FREQ_SLIDER_MIN, FREQ_SLIDER_MAX],
        slide: function(event, ui) {
          return _this.set_freq_range(event, ui);
        }
      });
      slider.append(slider_div);
      slider.css('float', 'left');
      slider.css('margin', '10px');
      sliders.append(slider);
      this.fft_range = [FREQ_SLIDER_MIN, FREQ_SLIDER_MAX];
      slider = $('<div></div>');
      slider.append($("<p>gain:</p>"));
      slider_div = $('<div id="gain-slider" style="height: 160px;"></div>');
      slider_div.slider({
        orientation: "vertical",
        animate: "fast",
        step: 0.1,
        min: GAIN_MIN,
        max: GAIN_MAX,
        value: GAIN_DEFAULT,
        slide: function(event, ui) {
          $("#gain").val(ui.value);
          return _this.gain = ui.value;
        }
      });
      slider.append(slider_div);
      slider.css('float', 'left');
      slider.css('margin', '10px');
      sliders.append(slider);
      controls.append(sliders);
      controls.css('float', 'left');
      $("#gain").val($("#gain-slider").slider("value"));
      div = $('<div></div>');
      $('body').append(div);
      myrender = function() {
        var foo, top_div;
        top_div = $('<div></div>');
        top_div.append(controls);
        _this.spec_plot.view.$el.css('float', 'left');
        top_div.append(_this.spec_plot.view.$el);
        div.append(top_div);
        foo = $('<div></div>');
        foo.append(_this.fft_plot.view.$el);
        foo.append(_this.power_plot.view.$el);
        foo.css('float', 'left');
        div.append(foo);
        div.append(_this.hist_plot.view.$el);
        _this.hist_plot.view.$el.css('float', 'left');
        _this.spec_plot.render();
        _this.power_plot.render();
        _this.fft_plot.render();
        return _this.hist_plot.render();
      };
      return _.defer(myrender);
    };

    return SpectrogramApp;

  })();

  SpectrogramPlot = (function() {
    function SpectrogramPlot(options) {
      var i, spec, _i, _ref;
      this.cmap = new LinearColorMapper.Model({
        palette: all_palettes["YlGnBu-9"],
        low: 0,
        high: 10
      });
      this.num_images = Math.ceil(NGRAMS / 500) + 3;
      this.image_width = 500;
      this.images = new Array(this.num_images);
      this.xs = new Array(this.num_images);
      for (i = _i = 0, _ref = this.num_images - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        this.images[i] = new ArrayBuffer(SPECTROGRAM_LENGTH * this.image_width * 4);
      }
      this.col = 0;
      this.source = Collections('ColumnDataSource').create({
        data: {
          image: this.images,
          x: this.xs
        }
      });
      spec = {
        type: 'image_rgba',
        x: 'x',
        y: 0,
        dw: this.image_width,
        dh: MAX_FREQ,
        cols: this.image_width,
        rows: SPECTROGRAM_LENGTH,
        image: 'image'
      };
      options = {
        title: "",
        dims: [options.width, options.height],
        xrange: [0, NGRAMS],
        yrange: [0, MAX_FREQ],
        xaxes: "min",
        yaxes: "min",
        xgrid: false,
        ygrid: false,
        tools: false
      };
      this.model = Bokeh.Plotting.make_plot(spec, this.source, options);
      this.view = new this.model.default_view({
        model: this.model
      });
    }

    SpectrogramPlot.prototype.update = function(fft) {
      var buf, buf32, i, image32, img, _i, _j, _ref, _ref1;
      buf = this.cmap.v_map_screen(fft);
      this.col -= 1;
      for (i = _i = 0, _ref = this.num_images - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        this.xs[i] += 1;
      }
      if (this.col === -1) {
        this.col = this.image_width - 1;
        img = this.images.pop();
        this.images = [img].concat(this.images.slice(0));
        this.xs.pop();
        this.xs = [-this.image_width + 1].concat(this.xs);
      }
      image32 = new Uint32Array(this.images[0]);
      buf32 = new Uint32Array(buf);
      for (i = _j = 0, _ref1 = SPECTROGRAM_LENGTH - 1; 0 <= _ref1 ? _j <= _ref1 : _j >= _ref1; i = 0 <= _ref1 ? ++_j : --_j) {
        image32[i * this.image_width + this.col] = buf32[i];
      }
      this.source.set('data', {
        image: this.images,
        x: this.xs
      });
      return this.source.trigger('change', this.source, {});
    };

    SpectrogramPlot.prototype.set_xrange = function(x0, x1) {
      return this.view.x_range.set({
        'start': x0,
        'end': x1
      });
    };

    SpectrogramPlot.prototype.set_yrange = function(y0, y1) {
      return this.view.y_range.set({
        'start': y0,
        'end': y1
      });
    };

    SpectrogramPlot.prototype.render = function() {
      return this.view.render();
    };

    return SpectrogramPlot;

  })();

  RadialHistogramPlot = (function() {
    function RadialHistogramPlot(options) {
      var spec;
      this.num_bins = options.num_bins;
      this.hist = new Float32Array(this.num_bins);
      this.source = Collections('ColumnDataSource').create({
        data: {
          inner_radius: [],
          outer_radius: [],
          start_angle: [],
          end_angle: [],
          fill_alpha: []
        }
      });
      spec = {
        type: 'annular_wedge',
        line_color: null,
        x: 0,
        y: 0,
        fill_color: '#688AB9',
        fill_alpha: 'fill_alpha',
        inner_radius: 'inner_radius',
        outer_radius: 'outer_radius',
        start_angle: 'start_angle',
        end_angle: 'end_angle'
      };
      options = {
        title: "",
        dims: [options.width, options.height],
        xrange: [-20, 20],
        yrange: [-20, 20],
        xaxes: false,
        yaxes: false,
        xgrid: false,
        ygrid: false,
        tools: false
      };
      this.model = Bokeh.Plotting.make_plot(spec, this.source, options);
      this.view = new this.model.default_view({
        model: this.model
      });
    }

    RadialHistogramPlot.prototype.update = function(fft, fft_min, fft_max) {
      var angle, bin_end, bin_max, bin_min, bin_size, bin_start, df, end, fill_alpha, i, inner, j, n, outer, start, vals, _i, _j, _k, _l, _ref, _ref1;
      df = FREQ_SLIDER_MAX - FREQ_SLIDER_MIN;
      bin_min = Math.floor(fft_min / df);
      bin_max = bin_min + Math.floor((fft_max - fft_min) / df * (fft.length - 1));
      bin_start = bin_min;
      bin_size = Math.ceil((bin_max - bin_min) / this.num_bins);
      for (i = _i = 0, _ref = this.num_bins - 1; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        this.hist[i] = 0;
        bin_end = Math.min(bin_start + bin_size - 1, bin_max);
        for (j = _j = bin_start; bin_start <= bin_end ? _j <= bin_end : _j >= bin_end; j = bin_start <= bin_end ? ++_j : --_j) {
          this.hist[i] += fft[j];
        }
        bin_start += bin_size;
      }
      inner = [];
      outer = [];
      start = [];
      end = [];
      fill_alpha = [];
      vals = [];
      angle = 2 * Math.PI / this.num_bins;
      for (i = _k = 0, _ref1 = this.hist.length - 1; 0 <= _ref1 ? _k <= _ref1 : _k >= _ref1; i = 0 <= _ref1 ? ++_k : --_k) {
        n = this.hist[i] / 16;
        for (j = _l = 0; 0 <= n ? _l <= n : _l >= n; j = 0 <= n ? ++_l : --_l) {
          vals.push(j);
          inner.push(2 + j);
          outer.push(2 + j + 0.95);
          start.push((i + 0.05) * angle);
          end.push((i + 0.95) * angle);
          fill_alpha.push(1 - 0.08 * j);
        }
      }
      this.source.set('data', {
        inner_radius: inner,
        outer_radius: outer,
        start_angle: start,
        end_angle: end,
        fill_alpha: fill_alpha
      });
      return this.source.trigger('change', this.source, {});
    };

    RadialHistogramPlot.prototype.render = function() {
      return this.view.render();
    };

    return RadialHistogramPlot;

  })();

  SimpleIndexPlot = (function() {
    function SimpleIndexPlot(options) {
      var spec;
      this.source = Collections('ColumnDataSource').create({
        data: {
          idx: [],
          ys: []
        }
      });
      spec = {
        type: 'line',
        line_color: 'darkblue',
        x: 'idx',
        y: 'ys'
      };
      options = {
        title: "",
        dims: [options.width, options.height],
        xrange: [options.x0, options.x1],
        yrange: [options.y0, options.y1],
        xaxes: "min",
        yaxes: "min",
        xgrid: false,
        tools: false
      };
      this.model = Bokeh.Plotting.make_plot(spec, this.source, options);
      this.view = new this.model.default_view({
        model: this.model
      });
    }

    SimpleIndexPlot.prototype.update = function(ys) {
      var i, _i, _ref, _ref1;
      if (((_ref = this.idx) != null ? _ref.length : void 0) !== ys.length) {
        this.idx = new Float64Array(ys.length);
        for (i = _i = 0, _ref1 = this.idx.length - 1; 0 <= _ref1 ? _i <= _ref1 : _i >= _ref1; i = 0 <= _ref1 ? ++_i : --_i) {
          this.idx[i] = this.view.x_range.get('start') + (i / this.idx.length) * this.view.x_range.get('end');
        }
      }
      this.source.set('data', {
        idx: this.idx,
        ys: ys
      });
      return this.source.trigger('change', this.source, {});
    };

    SimpleIndexPlot.prototype.set_xrange = function(x0, x1) {
      return this.view.x_range.set({
        'start': x0,
        'end': x1
      });
    };

    SimpleIndexPlot.prototype.set_yrange = function(y0, y1) {
      return this.view.y_range.set({
        'start': y0,
        'end': y1
      });
    };

    SimpleIndexPlot.prototype.render = function() {
      return this.view.render();
    };

    return SimpleIndexPlot;

  })();

  $(document).ready(function() {
    var spec;
    spec = new SpectrogramApp();
    return setInterval((function() {
      return spec.request_data();
    }), 400);
  });

}).call(this);
