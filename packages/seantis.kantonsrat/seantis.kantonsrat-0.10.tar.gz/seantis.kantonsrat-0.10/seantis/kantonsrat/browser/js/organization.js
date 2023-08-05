load_libraries(['_', 'jQuery', 'URI'], function(_, $, URI) {

    var enable_form_overlays = function(selector, before_close) {
        $(selector).prepOverlay({
            subtype: 'ajax',
            filter: '#content > *',
            formselector: 'form',
            closeselector: '[name="form.buttons.cancel"]',
            noform: function() {
                if (before_close) {
                    before_close();
                }
                return 'close';
            },
            config: {
                onBeforeLoad : function (e) {
                    var target = $(e.target);
                    if (! target.find('form').length) {
                        e.preventDefault();
                        reload_memberships();
                    } else {
                        // make sure the contenttree popup works inside the overlay
                        target.find('.searchButton').click(function() {
                            $('.overlay').hide();
                            $('#exposeMask').hide();

                            $('.contenttreeWindow').find(
                                '.contenttreeWindowActions input'
                            ).click(function() {
                                $('.overlay').show();
                                $('#exposeMask').show();
                            });
                        });
                    }
                }
            }
        });
    };

    var make_sortable = function(selector) {

        $(selector).hover(function(){
            $(this).css({ cursor: 'move' });
        }, function(){
            $(this).css({ cursor: 'auto' });
        });

        $(selector).sortable({
            placeholder: "ui-state-highlight",
            forcePlaceholderSize: true,
            axis: "y",
            update: function( event, ui ) {
                var uri = URI(window.location.href);
                var params = uri.query(true);

                var new_order = _.map($('.kantonsrat-memberships li'),
                    function(item) {
                        return item.id;
                    }
                );

                uri.segment('reorder-memberships');
                params['order'] = new_order.join(',');

                $.get(uri.query(params).toString()).fail(function() {
                    $(ui.sender).sortable('cancel');
                });
            }
        });
    };

    var reload_memberships = function() {
        var url = document.URL +  ' #kantonsrat-memberships-block';
        $('#kantonsrat-memberships-block').load(url, function() {
            setup_events();

            // firefox will sometimes fail to do this
            $('#ajax-spinner').hide();
        });
    };

    var setup_events = function() {
        if (_.isUndefined($.ui.autocomplete)) {
            enable_form_overlays('.kantonsrat-actions a', reload_memberships);
            enable_form_overlays(
                'a.contenttype-seantis-kantonsrat-membership', reload_memberships
            );
        } else {
            if (!_.isUndefined(console.log)) {
                console.log('jquery ui autocomplete is incompatible with plone');
                console.log('you should disable it through the settings for now');
                console.log('otherwise lots of overlays will not work');
            }
        }

        make_sortable('.userrole-manager .kantonsrat-memberships ul');
    };

    $(document).ready(function() {
        setup_events();
    });
});