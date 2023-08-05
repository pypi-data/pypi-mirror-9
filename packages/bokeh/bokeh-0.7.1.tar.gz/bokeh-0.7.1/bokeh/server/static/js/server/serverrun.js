(function() {
  define(["common/base", "./serverutils", "./usercontext/usercontext", "common/has_properties"], function(base, serverutils, usercontext, HasProperties) {
    var Config, Promises, load, load_one_object, reload, _render, _render_all, _render_one;
    Config = base.Config;
    Promises = serverutils.Promises;
    Config.ws_conn_string = "ws://" + window.location.host + "/bokeh/sub";
    reload = function() {
      var ping_url;
      Config = require("common/base").Config;
      ping_url = "" + Config.prefix + "bokeh/ping";
      $.get(ping_url).success(function() {
        console.log('reloading');
        return window.location.reload();
      }).fail(_.delay((function() {
        return reload();
      }), 1000));
      return null;
    };
    load_one_object = function(docid, objid) {
      HasProperties.prototype.sync = Backbone.sync;
      return $(function() {
        var resp, wswrapper;
        wswrapper = serverutils.utility.make_websocket();
        resp = serverutils.utility.load_one_object_chain(docid, objid);
        resp.done(function(data) {
          var model, view;
          model = base.Collections(data.type).get(objid);
          view = new model.default_view({
            model: model
          });
          return _render(view.el);
        });
        wswrapper.subscribe("debug:debug", "");
        return wswrapper.on('msg:debug:debug', function(msg) {
          if (msg === 'reload') {
            return reload();
          }
        });
      });
    };
    load = function(title) {
      HasProperties.prototype.sync = Backbone.sync;
      return $(function() {
        var userdocs, wswrapper;
        wswrapper = serverutils.utility.make_websocket();
        userdocs = new usercontext.UserDocs();
        userdocs.subscribe(wswrapper, 'defaultuser');
        window.userdocs = userdocs;
        load = userdocs.fetch();
        load.done(function() {
          if (title != null) {
            return _render_one(userdocs, title);
          } else {
            return _render_all(userdocs);
          }
        });
        console.log('subscribing to debug');
        wswrapper.subscribe("debug:debug", "");
        return wswrapper.on('msg:debug:debug', function(msg) {
          if (msg === 'reload') {
            return reload();
          }
        });
      });
    };
    _render_all = function(userdocs) {
      var userdocsview;
      userdocsview = new usercontext.UserDocsView({
        collection: userdocs
      });
      return _render(userdocsview.el);
    };
    _render_one = function(userdocs, title) {
      var doc, msg;
      doc = userdocs.find(function(doc) {
        return doc.get('title') === title;
      });
      if (doc != null) {
        doc.on('loaded', function() {
          var plot_context, plot_context_view;
          plot_context = doc.get('plot_context');
          plot_context_view = new plot_context.default_view({
            model: plot_context
          });
          return _render(plot_context_view.el);
        });
        return doc.load();
      } else {
        msg = "Document '" + title + "' wasn't found on this server.";
        _render(msg);
        return console.error(msg);
      }
    };
    _render = function(html) {
      return $('#PlotPane').append(html);
    };
    return {
      load: load,
      load_one_object: load_one_object
    };
  });

}).call(this);

/*
//@ sourceMappingURL=serverrun.js.map
*/