require({cache:{
'url:app/templates/FilteredGrid.html':"<div>\n\n    <div id=\"filter-wrapper\">\n        Filters:\n        <input id=\"filterNode\"/>\n        <input id=\"typeNode\"/>\n    </div>\n    <div id=\"gridNode\"></div>\n\n</div>"}});
define([
    "dojo/_base/declare",
    "dojo/on",
    "dojo/topic",
    "dojo/_base/lang",

    "dijit/_Widget",
    "dijit/_TemplatedMixin",
    "dijit/_WidgetsInTemplateMixin",
    "dojo/text!./templates/FilteredGrid.html",

    "dijit/form/ComboBox",
    "dijit/form/TextBox",
    "dijit/form/Button",
    "dijit/Menu",
    "dijit/MenuItem",
    "dijit/ConfirmDialog",
    "dojo/store/JsonRest",
    "dojo/store/Memory",
    "dojo/store/Cache",
    "dojo/store/Observable",
    "dgrid/OnDemandGrid", "dgrid/Selection", "dgrid/Keyboard", "dgrid/editor"

], function (declare, on, topic, lang, _Widget, _TemplatedMixin, _WidgetsInTemplateMixin, template, ComboBox,
             TextBox, Button, Menu, MenuItem, ConfirmDialog, JsonRest, Memory, Cache, Observable,
             OnDemandGrid, Selection, Keyboard, editor) {
    return declare([_Widget, _TemplatedMixin, _WidgetsInTemplateMixin], {
        templateString: template,

        concepttypes: null,
        conceptStore: null,
        conceptScheme: null,

        typeCombo: null,
        textFilter: null,
        conceptGrid: null,
        conceptFilter: {label: "", type: "all"},
        isResettingFilters: true,

        postCreate: function () {
            this.inherited(arguments);

            this.concepttypes = new Memory({
                data: [
                    {name: "All", id: "all"},
                    {name: "Concepts", id: "concept"},
                    {name: "Collections", id: "collection"}
                ]});
        },

        startup: function () {
            this.inherited(arguments);
            var self = this;
            var timeoutId;

            this.typeCombo = new ComboBox({
                id: "typeSelect",
                name: "ctype",
                store: this.concepttypes,
                searchAttr: "id",
                placeHolder: 'filter by type'
            }, "typeNode");

            this.textFilter = new TextBox({
                id: "labelFilter",
                name: "labelFilter",
                placeHolder: 'filter by label',
                intermediateChanges: true
            }, "filterNode");

            var columns = [
                {label: "ID", field: "id"},
                {label: "label", field: "label"},
                {label: "Type", field: "type"},
                {label: "URI", field: "uri"}

            ];

            this.conceptGrid = new (declare([OnDemandGrid, Selection, Keyboard]))({
                sort: "id",
                columns: columns,
                selectionMode: "single",
                minRowsPerPage: 20,
                maxRowsPerPage: 100
            }, "gridNode");

            on(this.conceptGrid, ".dgrid-row:click", lang.hitch(this, function (evt) {
                var row = this.conceptGrid.row(evt);
                row.scheme = this.conceptScheme;
                topic.publish("concept.open", row.id, row.scheme);
            }));

            this.conceptGrid.on(".dgrid-row:contextmenu", lang.hitch(this, function (evt) {
                evt.preventDefault(); // prevent default browser context menu
                var cell = this.conceptGrid.cell(evt);
                var gridId = this.conceptGrid.get("id");
                var pMenu = this._createGridContextMenu(gridId, cell.element, this, cell.row.data.id, cell.row.data.type, cell.row.data.label);
                pMenu._scheduleOpen(this, null, { x: evt.pageX, y: evt.pageY });
            }));

            on(this.typeCombo, "change", lang.hitch(this, function (evt) {
                if (evt != "") {
                    this._setTypeFilter(evt);
                }
            }));

            this.textFilter.watch("value", (lang.hitch(this, function (name, oldValue, newValue) {
                if (this.isResettingFilters) return false;
                if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                }
                timeoutId = setTimeout(lang.hitch(this, function () {
                    this._setTextFilter(newValue);
                }, 300));
                return true;
            })));
        },

        _resetFilters: function () {
            this.isResettingFilters = true;
            this.typeCombo.reset();
            this.textFilter.reset();
            this.conceptFilter = {label: "", type: "all"};
            this.isResettingFilters = false;
        },

        setScheme: function (schemeid) {
            this._resetFilters();
            this.conceptScheme = schemeid;
            this.conceptStore = new Observable( Cache( JsonRest({
                'target': "/conceptschemes/" + schemeid + "/c",
                'idProperty': 'id',
                'sortParam': 'sort',
                'accepts': 'application/json'
            }), Memory()));
            this.conceptGrid.set("store", this.conceptStore, this.conceptFilter);
        },

        ResetConceptGrid: function () {
            this._resetFilters();
            this.conceptStore = null;
            this.conceptGrid.set("store", this.conceptStore, this.conceptFilter);

        },

        _setTypeFilter: function (type) {
            this.conceptFilter = {label: this.conceptFilter.label, type: type};
            this.conceptGrid.set("query", this.conceptFilter);
        },

        _setTextFilter: function (label) {
            this.conceptFilter = {label: label, type: this.conceptFilter.type};
            this.conceptGrid.set("query", this.conceptFilter);
        },

        _createGridContextMenu: function (targetNodeId, selector, widget, conceptId, type, label) {
            var pMenu = new Menu({});

            if (type == "concept") {
                pMenu.addChild(new MenuItem({
                    label: "Add narrower concept",
                    onClick: function () {
                        topic.publish("concept.addNarrower", conceptId, label);
                    }
                }));
                pMenu.addChild(new MenuItem({
                    label: "Add subordinate array",
                    onClick: function () {
                        console.log('add sub array');
                        topic.publish("concept.addSubordinateArray", conceptId, label);
                    }
                }));
            }

            else if (type = "collection") {
                pMenu.addChild(new MenuItem({
                    label: "Add member",
                    onClick: function () {
                        topic.publish("concept.addMemberOf", conceptId, label);
                    }
                }));
            }

            pMenu.addChild(new MenuItem({
                label: "Edit",
                onClick: function () {
                    widget._editConcept(conceptId);
                }
            }));

            pMenu.addChild(new MenuItem({
                label: "Delete",
                onClick: function () {
                    widget._deleteConcept(conceptId, type, label);
                }
            }));

            pMenu.addChild(new dijit.MenuSeparator());
            pMenu.addChild(new MenuItem({
                label: "Add a new Concept or collection",
                onClick: function () {
                    widget._createNewConcept();
                }
            }));

          return pMenu;
        },


        _addNarrower: function (conceptId, type, label) {
            topic.publish("concept.addNarrower", conceptId, type, label);
        },

        _addMemberOf: function (conceptId, type, label) {
            topic.publish("concept.addMemberOf", conceptId, type, label);
        },

        _editConcept: function (conceptId) {
            topic.publish("concept.edit", conceptId);
        },

        _createNewConcept: function () {
            topic.publish("concept.create");
        },

        _deleteConcept: function (conceptId, type, label) {

            var myDialog = new ConfirmDialog({
                title: "Delete",
                content: "Are you sure you want to delete the " + type + " with the label " + label + " ?",
                style: "width: 200px"
            });

            on(myDialog, "execute", function () {
                topic.publish("concept.delete", conceptId);
            });
            on(myDialog, "cancel", function () {
                //do nothing, will be destroyed on hide
            });
            on(myDialog, "hide", function () {
                myDialog.destroyRecursive();
            });
            myDialog.show();

        }
    });

});
