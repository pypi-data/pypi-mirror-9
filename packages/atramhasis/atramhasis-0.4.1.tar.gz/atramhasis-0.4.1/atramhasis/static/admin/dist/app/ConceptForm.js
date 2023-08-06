require({cache:{
'url:app/templates/ConceptForm.html':"\n    <form data-dojo-attach-point='containerNode' style=\"height:420px;width: 720px;overflow:scroll;\">\n\n        <div data-dojo-attach-point=\"formNode\" class=\"cFormDialog\">\n            <div data-dojo-attach-point=\"MyTable\"></div>\n            <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'labels', open:true\">\n                <div data-dojo-attach-point=\"labelContainerNode\"></div>\n            </div>\n\n            <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'notes', open:true\">\n                <div data-dojo-attach-point=\"noteContainerNode\"></div>\n            </div>\n            <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'relations', open:true\">\n                <div data-dojo-attach-point=\"broaderContainerNode\"></div>\n                <div data-dojo-attach-point=\"narrowerContainerNode\"></div>\n                <div data-dojo-attach-point=\"relatedContainerNode\"></div>\n                <div data-dojo-attach-point=\"membersContainerNode\"></div>\n                <div data-dojo-attach-point=\"memberofContainerNode\"></div>\n                <div data-dojo-attach-point=\"subordinateArraysContainerNode\"></div>\n                <div data-dojo-attach-point=\"superordinatesContainerNode\"></div>\n            </div>\n            <div data-dojo-type=\"dijit/TitlePane\" data-dojo-props=\"title: 'matches', open:true\">\n                <div data-dojo-attach-point=\"matchesContainerNode\"></div>\n            </div>\n            <div class=\"dijitDialogPaneActionBar\" style=\"width: 700px\">\n                <button data-dojo-type='dijit/form/Button' type='submit'>save</button>\n                <button data-dojo-type='dijit/form/Button' data-dojo-attach-event=\"onClick:onCancel\">cancel</button>\n            </div>\n        </div>\n    </form>\n"}});
define(
    [
        'dojo/_base/declare',
        "dojo/_base/array",
        "dojo/topic", "dojo/on", "dojo/dom-construct", "dojo/query",
        "dojo/store/Memory",
        "dijit/registry",
        'dijit/_WidgetBase', 'dijit/_TemplatedMixin',
        'dijit/form/Form', "dijit/form/CheckBox",
        'dijit/_WidgetsInTemplateMixin',
        'dojox/form/manager/_Mixin', 'dojox/form/manager/_NodeMixin', 'dojox/form/manager/_FormMixin', 'dojox/form/manager/_DisplayMixin',
        "dojo/text!./templates/ConceptForm.html",
        "./form/LabelManager",
        "./form/NoteManager",
        "./form/RelationManager",
        "./form/MatchesManager",
        'dijit/form/Select',
        'dijit/form/FilteringSelect',
        'dijit/form/ValidationTextBox', 'dojox/validate', 'dijit/form/NumberTextBox',
        'dijit/form/Button',
        'dojo/dom-form',
        'dojox/layout/TableContainer',
        'dijit/form/TextBox',
        'dijit/form/ComboBox'
    ],
    function (declare, arrayUtil, topic, on, domConstruct, query, Memory, registry, _WidgetBase, _TemplatedMixin, Form, CheckBox, WidgetsInTemplateMixin, FormMgrMixin, FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin, template, LabelManager, NoteManager, RelationManager, MatchesManager, Select, FilteringSelect, ValidationTextBox, Validate, NumberTextBox, Button, domForm, TableContainer, TextBox, ComboBox) {
        return declare([
                Form, _WidgetBase, WidgetsInTemplateMixin, _TemplatedMixin, FormMgrMixin,
                FormMgrNodeMixin, FormMgrFormMixin, FormMgrDisplayMixin
            ], {
                templateString: template,
                widgetsInTemplate: true,
                dialog: null,
                scheme: null,
                typeComboBox: null,
                conceptId: null,
                thesauri: null,
                externalSchemeService: null,
                languageStore: null,

                constructor: function (options) {
                    declare.safeMixin(this, options);
                    this.inherited(arguments)
                },
                postCreate: function () {
                    this.inherited(arguments);
                    this.labelManager = new LabelManager({
                        'name': 'lblMgr',
                        'languageStore': this.languageStore
                    }, this.labelContainerNode);
                    this.noteManager = new NoteManager({
                        'name': 'noteMgr',
                        'languageStore': this.languageStore
                    }, this.noteContainerNode);
                    this.broaderManager = new RelationManager({
                        'name': 'broaderMgr',
                        'title': 'Broader',
                        'scheme': this.scheme
                    }, this.broaderContainerNode);
                    this.narrowerManager = new RelationManager({
                        'name': 'narrowerMgr',
                        'title': 'Narrower',
                        'scheme': this.scheme
                    }, this.narrowerContainerNode);
                    this.relatedManager = new RelationManager({
                        'name': 'relatedMgr',
                        'title': 'Related',
                        'scheme': this.scheme
                    }, this.relatedContainerNode);
                    this.membersManager = new RelationManager({
                        'name': 'membersMgr',
                        'title': 'Members',
                        'scheme': this.scheme,
                        'style': 'display: none'
                    }, this.membersContainerNode);
                    this.memberofManager = new RelationManager({
                        'name': 'memberofMgr',
                        'title': 'Member of',
                        'scheme': this.scheme
                    }, this.memberofContainerNode);
                    this.subordinateArraysManager = new RelationManager({
                        'name': 'subordinateArraysMgr',
                        'title': 'Subordinate Arrays',
                        'scheme': this.scheme
                    }, this.subordinateArraysContainerNode);
                    this.superordinatesManager = new RelationManager({
                        'name': 'superordinatesMgr',
                        'title': 'Superordinates',
                        'scheme': this.scheme,
                        'style': 'display: none'
                    }, this.superordinatesContainerNode);
                    this.matchesManager = new MatchesManager({
                        'name': 'matchesMgr',
                        'title': 'Match',
                        'scheme': this.scheme,
                        'thesauri': this.thesauri,
                        'externalSchemeService': this.externalSchemeService
                    }, this.matchesContainerNode);
                    var myTable = new TableContainer({cols: 2, spacing: 10}, this.MyTable);
                    var schemebox = new TextBox({id: "schemebox", title: "Scheme:"});
                    schemebox.set('disabled', true);
                    var typeStore = new Memory({
                        data: [
                            {name: "concept", id: "concept"},
                            {name: "collection", id: "collection"}
                        ]
                    });

                    var typeComboBox = new ComboBox({
                        id: "typecombobox",
                        name: "ctype",
                        store: typeStore,
                        searchAttr: "name",
                        title: "Type:",
                        value: "concept"
                    });
                    var self = this;
                    typeComboBox.on("change", function () {
                        var val = this.get('value');
                        if (val == 'collection') {
                            self.broaderManager.close();
                            self.narrowerManager.close();
                            self.relatedManager.close();
                            self.membersManager.open();
                            self.memberofManager.open();
                            self.matchesManager.close();
                            self.subordinateArraysManager.close();
                            self.superordinatesManager.open();
                        }
                        else if (val == 'concept') {
                            self.broaderManager.open();
                            self.narrowerManager.open();
                            self.relatedManager.open();
                            self.membersManager.close();
                            self.memberofManager.open();
                            self.matchesManager.open();
                            self.subordinateArraysManager.open();
                            self.superordinatesManager.close();
                        }
                    });
                    this.typeComboBox = typeComboBox;
                    typeComboBox.startup();
                    // Add the 3 text boxes to the TableContainer
                    myTable.addChild(schemebox);
                    myTable.addChild(typeComboBox);
                    myTable.startup();

                    on(this, "reset", function () {
                        self._resetWidgets();
                        self.conceptId = null;
                    });
                },
                startup: function () {
                    this.inherited(arguments);
                },
                onSubmit: function (evt) {
                    evt.preventDefault();
                    this.inherited(arguments);
                    this.validate();
                    if (this.isValid()) {
                        var formObj = domForm.toObject(this.containerNode);
                        formObj.concept_id = this.conceptId;
                        formObj.broader = this.broaderManager.getRelations();
                        formObj.narrower = this.narrowerManager.getRelations();
                        formObj.related = this.relatedManager.getRelations();
                        formObj.members = this.membersManager.getRelations();
                        formObj.member_of = this.memberofManager.getRelations();
                        formObj.subordinate_arrays = this.subordinateArraysManager.getRelations();
                        formObj.superordinates = this.superordinatesManager.getRelations();
                        formObj.label = this.labelManager.getLabels();
                        formObj.note = this.noteManager.geNotes();
                        if (this.matchesManager.getMatches()){
                            formObj.matches = this.matchesManager.getMatches();
                        }
                        console.log(formObj);
                        topic.publish("conceptform.submit", formObj);
                    }
                    this.dialog && this.dialog.layout();

                    return false;
                },
                onCancel: function () {
                    //hide implemented on dialog level
                },
                _resetWidgets: function () {
                    this.broaderManager.reset("Broader");
                    this.narrowerManager.reset("Narrower");
                    this.relatedManager.reset("Related");
                    this.membersManager.reset("Members");
                    this.memberofManager.reset("Member of");
                    this.subordinateArraysManager.reset("Subordinate Arrays");
                    this.superordinatesManager.reset("Superordinates");
                    this.labelManager.reset();
                    this.noteManager.reset();
                    this.matchesManager.reset();
                },

                init: function (scheme, concept) {
                    console.log("init cdialog: " + scheme);
                    this.reset();
                    this.scheme = scheme;
                    var schemebox = dijit.byId("schemebox");
                    schemebox.set('value', scheme);
                    this.broaderManager.setScheme(scheme);
                    this.narrowerManager.setScheme(scheme);
                    this.relatedManager.setScheme(scheme);
                    this.membersManager.setScheme(scheme);
                    this.memberofManager.setScheme(scheme);
                    this.subordinateArraysManager.setScheme(scheme);
                    this.superordinatesManager.setScheme(scheme);
                    if (concept) {
                        console.log("editing existing concept: " + concept.label);
                        this.conceptId = concept.id;
                        this.typeComboBox.set("value", concept.type);
                        if (concept.members) {
                            this.membersManager.setRelations(concept.members);
                        }
                        if (concept.member_of)
                        {
                         this.memberofManager.setRelations(concept.member_of);

                        }
                        if (concept.broader)
                        {
                            this.broaderManager.setRelations(concept.broader);
                        }
                        if (concept.narrower)
                        {
                            this.narrowerManager.setRelations(concept.narrower);
                        }
                        if (concept.related)
                        {
                            this.relatedManager.setRelations(concept.related);
                        }
                        if (concept.subordinate_arrays)
                        {
                            this.subordinateArraysManager.setRelations(concept.subordinate_arrays);
                        }
                        if (concept.superordinates)
                        {
                            this.superordinatesManager.setRelations(concept.superordinates);
                        }
                        if (concept.labels) {
                            this.labelManager.setLabels(concept.labels);
                                    if(concept.labels.length>0) {
                                        this.labelManager.SetEditLabelButton();
                                    }
                        }
                        if (concept.notes)
                        {
                            this.noteManager.setNotes(concept.notes);
                            if(concept.notes.length>0) {
                                this.noteManager.setEditNoteButton();
                            }
                        }
                        if(concept.matches)
                        {
                            this.matchesManager.setMatchUris(concept.matches);
                        }
                    }
                    this.dialog && this.dialog.layout();
                },
                addBroader: function (broader) {
                    console.log("add existing broader: " + broader.label);
                    this.broaderManager.setRelations(broader);
                },
                addMemberOf: function (memberOf) {
                    console.log("add existing broader: " + memberOf.label);
                    this.memberofManager.setRelations(memberOf);
                }
            }
        )
    }
);
