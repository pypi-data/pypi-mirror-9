(function() {
  var __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  define(["underscore", "jquery", "handsontable", "backbone", "common/has_properties", "common/continuum_view"], function(_, $, $$1, Backbone, HasProperties, ContinuumView) {
    var HandsonTable, HandsonTableView, HandsonTables, _ref, _ref1, _ref2;
    HandsonTableView = (function(_super) {
      __extends(HandsonTableView, _super);

      function HandsonTableView() {
        _ref = HandsonTableView.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      HandsonTableView.prototype.initialize = function(options) {
        HandsonTableView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change:source', this.render);
      };

      HandsonTableView.prototype.render = function() {
        var column, columns, data, headers, ht, source, type, _i, _len, _ref1,
          _this = this;
        source = this.mget("source");
        if (source != null) {
          headers = [];
          columns = [];
          _ref1 = this.mget("columns");
          for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
            column = _ref1[_i];
            headers.push(column.get("header"));
            data = column.get("data");
            type = column.get("type");
            columns.push({
              data: data,
              type: type
            });
          }
          this.$el.handsontable({
            data: source.datapoints(),
            colHeaders: headers,
            columns: columns,
            afterChange: function(changes, source) {
              if (source === "edit") {
                return _this.editData(changes);
              }
            }
          });
          ht = this.$el.handsontable("getInstance");
          return ht.view.wt.draw(true);
        } else {
          return this.$el.handsontable();
        }
      };

      HandsonTableView.prototype.editData = function(changes) {
        var array, change, column, data, i, index, new_val, old_val, source, _i, _j, _len, _ref1;
        source = this.mget("source");
        data = source.get("data");
        for (_i = 0, _len = changes.length; _i < _len; _i++) {
          change = changes[_i];
          index = change[0], column = change[1], old_val = change[2], new_val = change[3];
          array = _.clone(data[column]);
          if (index < array.length) {
            array[index] = new_val;
          } else {
            for (i = _j = 0, _ref1 = array.length - index; 0 <= _ref1 ? _j < _ref1 : _j > _ref1; i = 0 <= _ref1 ? ++_j : --_j) {
              array.push(NaN);
            }
            array.push(new_val);
          }
          data[column] = array;
        }
        return source.set(data);
      };

      return HandsonTableView;

    })(ContinuumView.View);
    HandsonTable = (function(_super) {
      __extends(HandsonTable, _super);

      function HandsonTable() {
        _ref1 = HandsonTable.__super__.constructor.apply(this, arguments);
        return _ref1;
      }

      HandsonTable.prototype.type = 'HandsonTable';

      HandsonTable.prototype.default_view = HandsonTableView;

      HandsonTable.prototype.defaults = function() {
        return {
          source: null,
          columns: []
        };
      };

      return HandsonTable;

    })(HasProperties);
    HandsonTables = (function(_super) {
      __extends(HandsonTables, _super);

      function HandsonTables() {
        _ref2 = HandsonTables.__super__.constructor.apply(this, arguments);
        return _ref2;
      }

      HandsonTables.prototype.model = HandsonTable;

      return HandsonTables;

    })(Backbone.Collection);
    return {
      Model: HandsonTable,
      Collection: new HandsonTables(),
      View: HandsonTableView
    };
  });

}).call(this);

/*
//@ sourceMappingURL=handson_table.js.map
*/