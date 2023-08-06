require({cache:{
'url:app/templates/ConceptDetail.html':"<div>\n    <div class=\"actionBar\">\n        <ul data-dojo-attach-point=\"actionNode\"></ul>\n    </div>\n\n    <h1 data-dojo-attach-point='nameNode'>${schemeid}: <i>${label}</i></h1>\n\n    <div class=\"conceptProps\">\n        <ul>\n            <li data-dojo-attach-point='idNode'>id: ${conceptid}</li>\n            <li data-dojo-attach-point='typeNode'>type: ${type}</li>\n            <li data-dojo-attach-point='uriNode'>uri: ${uri}</li>\n        </ul>\n    </div>\n\n    <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'labels', open:true\">\n        <div data-dojo-attach-point=\"prefLabelListNode\"></div>\n        <div data-dojo-attach-point=\"altLabelListNode\"></div>\n        <div data-dojo-attach-point=\"hiddenLabelListNode\"></div>\n    </div>\n\n    <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'notes', open:true\">\n        <div data-dojo-attach-point=\"changeNoteListNode\"></div>\n        <div data-dojo-attach-point=\"definitionListNode\"></div>\n        <div data-dojo-attach-point=\"editorialNoteListNode\"></div>\n        <div data-dojo-attach-point=\"exampleListNode\"></div>\n        <div data-dojo-attach-point=\"historyNoteListNode\"></div>\n        <div data-dojo-attach-point=\"scopeNoteListNode\"></div>\n        <div data-dojo-attach-point=\"noteListNode\"></div>\n    </div>\n\n    <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'relations', open:true\">\n        <div data-dojo-attach-point=\"broaderListNode\"></div>\n        <div data-dojo-attach-point=\"narrowerListNode\"></div>\n        <div data-dojo-attach-point=\"relatedListNode\"></div>\n        <div data-dojo-attach-point=\"membersListNode\"></div>\n        <div data-dojo-attach-point=\"memberofListNode\"></div>\n        <div data-dojo-attach-point=\"subordinateArraysListNode\"></div>\n        <div data-dojo-attach-point=\"superordinatesListNode\"></div>\n    </div>\n\n    <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'matches', open:true\">\n        <div data-dojo-attach-point=\"broadMatchListNode\"></div>\n        <div data-dojo-attach-point=\"closeMatchListNode\"></div>\n        <div data-dojo-attach-point=\"exactMatchListNode\"></div>\n        <div data-dojo-attach-point=\"narrowMatchListNode\"></div>\n        <div data-dojo-attach-point=\"relatedMatchListNode\"></div>\n    </div>\n\n\n\n</div>"}});
define([
    'dojo/_base/declare',
    "dojo/_base/array",
    "dojo/dom-construct",
    "dojo/dom-attr",
    "dojo/dom-class",
    "dojo/on",
    "dojo/topic",
    'dijit/_WidgetBase',
    'dijit/_TemplatedMixin',
    'dijit/_WidgetsInTemplateMixin',
    "dijit/ConfirmDialog",
    "dijit/Dialog",
    "dijit/form/Button",
    "./form/ConceptDetailList",
    'dojo/text!./templates/ConceptDetail.html',
    "dijit/TitlePane",
    "dgrid/List",
    "dgrid/Keyboard",
    "dgrid/Selection",
    "dgrid/extensions/DijitRegistry"
], function (declare, arrayUtil, domConstruct, domAttr, domClass, on, topic, _WidgetBase, _TemplatedMixin,
             _WidgetsInTemplateMixin, ConfirmDialog, Dialog, Button, ConceptDetailList, template, TitlePane,
             dgridList, dgridKeyboard, dgridSelection, DijitRegistry) {
    return declare([_WidgetBase, _TemplatedMixin, _WidgetsInTemplateMixin], {

        templateString: template,

        baseClass: "conceptDetail",
        listNode: this.labelNode,
        conceptid: "",
        label: "",
        type: "",
        uri: "",
        schemeid: "",
        labels: [],
        notes: [],
        narrower: [],
        related: [],
        broader: [],
        members: [],
        member_of: [],
        subordinate_arrays: [],
        superordinates: [],
        matches: null,
        matchUris: [],
        externalSchemeService: null,
        _mergeDialog: null,
        _mergeButton: null,


        postCreate: function () {

            this.matches = [];
            this.prefLabelList = new ConceptDetailList({ }, this.prefLabelListNode);
            this.altLabelList = new ConceptDetailList({}, this.altLabelListNode);
            this.hiddenLabelList = new ConceptDetailList({}, this.hiddenLabelListNode);
            this.changeNoteList = new ConceptDetailList({ }, this.changeNoteListNode);
            this.definitionList = new ConceptDetailList({}, this.definitionListNode);
            this.editorialNoteList = new ConceptDetailList({}, this.editorialNoteListNode);
            this.exampleList = new ConceptDetailList({ }, this.exampleListNode);
            this.historyNoteList = new ConceptDetailList({}, this.historyNoteListNode);
            this.scopeNoteList = new ConceptDetailList({}, this.scopeNoteListNode);
            this.noteList = new ConceptDetailList({}, this.noteListNode);
            this.broaderList = new ConceptDetailList({}, this.broaderListNode);
            this.narrowerList = new ConceptDetailList({}, this.narrowerListNode);
            this.relatedList = new ConceptDetailList({}, this.relatedListNode);
            this.membersList = new ConceptDetailList({}, this.membersListNode);
            this.memberofList = new ConceptDetailList({}, this.memberofListNode);
            this.subordinateArraysList = new ConceptDetailList({}, this.subordinateArraysListNode);
            this.superordinatesList = new ConceptDetailList({}, this.superordinatesListNode);
            this.broadMatchList = new ConceptDetailList({}, this.broadMatchListNode);
            this.closeMatchList = new ConceptDetailList({}, this.closeMatchListNode);
            this.exactMatchList = new ConceptDetailList({}, this.exactMatchListNode);
            this.narrowMatchList = new ConceptDetailList({}, this.narrowMatchListNode);
            this.relatedMatchList = new ConceptDetailList({}, this.relatedMatchListNode);

            this._CreateNodeLists();

            var actionNode = this.actionNode;
            var deleteLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Delete</a>"
            }, actionNode);
            var editLi = domConstruct.create("li", {
                innerHTML: "<a href='#'>Edit</a>"
            }, actionNode);
            if (this.type == 'concept') {
                var mergeLi = domConstruct.create("li", {
                  innerHTML: "<a href='#'>Merge</a>"
                }, actionNode);
                this._mergeButton = mergeLi;

                //set disabled when no matches are defined
                domClass.add(this._mergeButton, "disabled");
                var types = this.externalSchemeService.matchTypes;
                arrayUtil.forEach(types, function(typeObj) {
                    var type = typeObj.value;
                    if (this.matchUris && this.matchUris[type]) {
                      domClass.remove(this._mergeButton, "disabled");
                    }
                }, this);
            }

            var self = this;
            on(deleteLi, "click", function (evt) {
                evt.preventDefault();

                var myDialog = new ConfirmDialog({
                    title: "Delete",
                    content: "Are you sure you want to delete this?",
                    style: "width: 200px"
                });
                on(myDialog, "execute", function () {
                    topic.publish("concept.delete", self.conceptid);
                });
                on(myDialog, "cancel", function () {
                    //do nothing, will be destroyed on hide
                });
                on(myDialog, "hide", function () {
                    myDialog.destroyRecursive();
                });
                myDialog.show();

                return false;
            });

            on(editLi, "click", function (evt) {
                evt.preventDefault();
                topic.publish("concept.edit", self.conceptid);
                return false;
            });

            if (this.type == 'concept') {
                on(mergeLi, "click", function (evt) {
                  evt.preventDefault();

                  if (domClass.contains(mergeLi, "disabled")) {
                    return false;
                  }

                  if (self.matches.length == 0) {
                    topic.publish('dGrowl', "No matches to merge (or matches are still loading)", {'title': "Warning", 'sticky': false, 'channel': 'warn'});
                    return false;
                  }
                  else {
                    if (!self._mergeDialog) {
                      self._mergeDialog = self._createMergeDialog();
                    }
                    self._mergeDialog.setMatches(self.matches);
                    self._mergeDialog.show();
                  }

                  return false;
                });
            }

        },
        _refreshConceptDetail:function(refreshedConcept)
        {
            this.labels=refreshedConcept.labels;
            this.notes=refreshedConcept.notes;
            this.broader=refreshedConcept.broader;
            this.narrower=refreshedConcept.narrower;
            this.related=refreshedConcept.related;
            this.members=refreshedConcept.members;
            this.member_of=refreshedConcept.member_of;
            this.subordinate_arrays=refreshedConcept.subordinate_arrays;
            this.superordinates=refreshedConcept.superordinates;
            this.matchUris=refreshedConcept.matches;
            this._CreateNodeLists();
        },

        _CreateNodeLists:function()
        {
            this.prefLabelList.buildList(this.prefLabelList.mapLabelsForList(this.labels, "prefLabel"), "Preferred labels", false);
            this.altLabelList.buildList(this.altLabelList.mapLabelsForList(this.labels, "altLabel"), "Alternate labels", false);
            this.hiddenLabelList.buildList( this.hiddenLabelList.mapLabelsForList(this.labels, "hiddenLabel"), "Hidden labels", false);

            this.definitionList.buildList(this.definitionList.mapNotesForList(this.notes, "definition"), "Definition", false);
            this.changeNoteList.buildList(this.changeNoteList.mapNotesForList(this.notes, "changeNote"), "Change note", false);
            this.editorialNoteList.buildList(this.editorialNoteList.mapNotesForList(this.notes, "editorialNote"), "Editorial note", false);
            this.exampleList.buildList( this.exampleList.mapNotesForList(this.notes, "example"), "Example", false);
            this.historyNoteList.buildList(this.historyNoteList.mapNotesForList(this.notes, "historyNote"), "Historynote", false);
            this.scopeNoteList.buildList(this.scopeNoteList.mapNotesForList(this.notes, "scopeNote"), "Scopenote", false);
            this.noteList.buildList(this.noteList.mapNotesForList(this.notes, "note"), "Note", false);

            this.broaderList.schemeid=this.schemeid;
            this.narrowerList.schemeid=this.schemeid;
            this.relatedList.schemeid=this.schemeid;
            this.membersList.schemeid=this.schemeid;
            this.memberofList.schemeid=this.schemeid;
            this.subordinateArraysList.schemeid=this.schemeid;
            this.superordinatesList.schemeid=this.schemeid;

            this.broaderList.buildList(this.broaderList.mapRelationsForList(this.broader), "Broader", true);
            this.narrowerList.buildList(this.narrowerList.mapRelationsForList(this.narrower), "Narrower", true);
            this.relatedList.buildList(this.relatedList.mapRelationsForList(this.related), "Related", true);
            this.membersList.buildList(this.membersList.mapRelationsForList(this.members), "Members", true);
            this.memberofList.buildList(this.memberofList.mapRelationsForList(this.member_of), "Member of", true);
            this.subordinateArraysList.buildList(this.subordinateArraysList.mapRelationsForList(this.subordinate_arrays), "Subordinate Arrays", true);
            this.superordinatesList.buildList(this.superordinatesList.mapRelationsForList(this.superordinates), "Superordinates", true);

            this._createMatchesLists();
        },

        _createMatchesLists: function () {
            this.matches = [];
            var types = this.externalSchemeService.matchTypes;
            var self = this;
            arrayUtil.forEach(types, function(typeObj) {
                var type = typeObj.value;
                if (self.matchUris && self.matchUris[type]) {
                    arrayUtil.forEach(self.matchUris[type], function(uri) {
                         var matchPromise = null;
                        try {
                            matchPromise = self.externalSchemeService.getMatch(uri, type);
                            matchPromise.then(function (match) {
                                self.matches.push(match);
                                if (type == 'broad') {
                                    self.broadMatchList.buildList(self.broadMatchList.mapMatchesForList(self.matches, type), "Broad Matches", false);
                                }
                                else if (type == 'close') {
                                    self.closeMatchList.buildList(self.closeMatchList.mapMatchesForList(self.matches, type), "Close Matches", false);
                                }
                                else if (type == 'exact') {
                                    self.exactMatchList.buildList(self.exactMatchList.mapMatchesForList(self.matches, type), "Exact Matches", false);
                                }
                                else if (type == 'narrow') {
                                    self.narrowMatchList.buildList(self.narrowMatchList.mapMatchesForList(self.matches, type), "Narrow Matches", false);
                                }
                                else if (type == 'related') {
                                    self.relatedMatchList.buildList(self.relatedList.mapMatchesForList(self.matches, type), "Related Matches", false);
                                }
                            }, function (err) {
                                topic.publish('dGrowl', err, {'title': "Error when looking up match", 'sticky': true, 'channel':'error'});
                            });
                        } catch(err) {
                            topic.publish('dGrowl', err, {'title': "Error when looking up match", 'sticky': true, 'channel':'error'});
                        }
                    });
                }
            }, this);
        },

        _createMergeDialog: function() {

            var self = this;

            var dlg = new Dialog({
                'class': "externalForm",
                'title': "Choose one or more matches"
            });

            //layout
            var matchDiv = domConstruct.create("div", {}, dlg.containerNode);

            domConstruct.create("p", {
                'innerHTML': "Select one or more matches to merge (hold ctrl or shift to select multiple items):"
            }, matchDiv);

            var listHolder = domConstruct.create("div", {}, matchDiv);
            var list = new (declare([dgridList, dgridKeyboard, dgridSelection, DijitRegistry]))({
                selectionMode: "single",
                renderRow: function(object){
                    return domConstruct.create("div", {
                        innerHTML: object.data.label + " (" + object.type + " match, uri: <em>" + object.data.uri + "</em>)"
                    });
                }
            }, listHolder);
            list.renderArray([]);

            var actionBar = domConstruct.create("div", {
                'class': "dijitDialogPaneActionBar",
                width: "300px"
            }, dlg.containerNode);

            var mergeBtn = new Button({
                "label": "Merge"
            }).placeAt(actionBar);

            var cancelBtn = new Button({
                "label": "Cancel"
            }).placeAt(actionBar);

            //behavior
            dlg.setMatches = function (matches) {
                list.renderArray(matches);
            };

            mergeBtn.onClick = function () {
                var rows = [];
                for (var id in list.selection) {
                    if (list.selection[id]) {
                        var row = list.row(id);
                        console.log("row 1 ", row);
                        rows.push(row);
                    }
                }
                if (rows.length == 0) {
                  topic.publish('dGrowl', "No matches selected", {'title': "Warning", 'sticky': false, 'channel': 'warn'});
                }
                else {
                  arrayUtil.forEach(rows, function (row) {
                      var object = row.data;
                      topic.publish('concept.merge', {'id': this.conceptid, 'match': object, 'schemeid': this.schemeid} );
                  }, self);

                  dlg.hide();
                }

            };

            cancelBtn.onClick = function () {
                dlg.hide();
            };

            on(dlg, "hide", function () {
                //reset stuff
                list.refresh();
            });

            return dlg
        }

    });
});
