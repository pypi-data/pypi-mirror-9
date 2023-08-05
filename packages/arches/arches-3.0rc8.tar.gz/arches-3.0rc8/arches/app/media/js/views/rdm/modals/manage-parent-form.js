define(['jquery', 'backbone', 'arches', 'views/concept-search', 'models/concept'], function ($, Backbone, arches, ConceptSearch, ConceptModel) {
    return Backbone.View.extend({

        events: {
            'click .modal-footer .savebtn': 'save',
            'click .modal-footer .btn-u-default': 'cancel',
            'click a': 'removeRelationship'
        },

        initialize: function(){
            var self = this;
            this.conceptsearch = new ConceptSearch({
                el:this.$el,
                getUrl: function(){
                    return arches.urls.concept_search + '?removechildren=' + self.model.get('id');
                }
            });
            this.modal = this.$el.find('.modal');
            this.relationshiptype = this.modal.find('#parent-relation-type').select2({
                minimumResultsForSearch: 10,
                maximumSelectionSize: 1
            });
            this.numberOfParents = this.$el.find('a').length;
            this.deletedrelationships = [];
        },
        
		save: function(){
            var self = this;
            if (this.conceptsearch.searchbox.val() !== ''){
                var parentConcept = new ConceptModel({
                    id: this.conceptsearch.searchbox.val(),
                    relationshiptype: this.relationshiptype.val()
                });
                this.model.set('added', [parentConcept.toJSON()]);
            }

            var concepts = [];
            $.each(this.deletedrelationships, function(){
                var parentConcept = new ConceptModel({
                    id: this
                });
                concepts.push(parentConcept);
            })
            self.model.set('deleted', concepts)

            this.model.save(function() {
                this.modal.modal('hide');
                $('.modal-backdrop.fade.in').remove();  // a hack for now
                this.cleanup();
            }, this);

        },

        cancel: function(){
            this.cleanup();
        },

        removeRelationship: function(e){
            var data = $(e.target).data();
            this.deletedrelationships.push(data.id);
            this.$el.find('[data-id="'+ data.id +'"]').toggle(300);

            if (this.deletedrelationships.length == this.numberOfParents - 1){
                this.$el.find('a').hide(300);
            }
        },

        cleanup: function() {
            var self = this;
            $.each(this.deletedrelationships, function(){
                self.$el.find('[data-id="'+ this +'"]').toggle(300);
            })
            this.model.set('deleted', []);
            this.model.set('added', []);

            this.$el.find('a').show(300);            
            this.undelegateEvents();
        }
    });
});