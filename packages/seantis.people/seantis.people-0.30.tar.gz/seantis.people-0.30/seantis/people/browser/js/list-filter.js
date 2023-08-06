load_libraries(['_', 'jQuery', 'URI'], function(_, $, URI) {
    "use strict";

     /*
        If a function is wrapped with the acquire_lock it cannot be called
        again as long as it is running.

        It stops this function from repeating forever:

        var infinite = function() {
            infinite();
        }
        infinite();

        By wrapping it:

        var infinite = function acquire_lock('infinite-lock', function() {
            infinite(); // will lead nowhere
        })
        infinite();

        The use for this function is to wrap event-handlers so they can change
        things on the dom without triggering another invocation of themselves.
    */
    var locked = {};
    var acquire_lock = function(id, inner_function) {
        if (! _.has(locked, id)) {
            locked[id] = false;
        }
        return function() {
            if (locked[id]) return;
            try {
                locked[id] = true;
                return inner_function.apply(this, arguments);
            } finally {
                locked[id] = false;
            }
        };
    };

    /*
        Creates a loader which loads urls using ajax, replacing the blocks
        with the class defined in options.fragments with the ones loaded in
        the request.

        The blocks need the 'loader-fragment' class and an identifer:

        <div class='loader-fragment' data-fragment-id='1' />
    */
    $.FragmentsLoader = function() {
        var self = {};
        var fragment_selector = '.loader-fragment';

        self.map_fragments = function(fragments) {
            return _.object(
                _.map(fragments, function(fragment) {
                    var f = $(fragment);
                    return [f.data('fragment-id'), f];
                })
            );
        };

        self.load = function(url) {
            var carrier = $('<div>');
            var selector = url + ' ' + fragment_selector;

            carrier.load(selector, function(data) {
                var local_fragments = self.map_fragments($(fragment_selector));
                var loaded_fragments = self.map_fragments(
                    $(carrier).find(fragment_selector)
                );

                _.each(loaded_fragments, function(fragment, id) {
                    if (_.has(local_fragments, id)) {
                        local_fragments[id].replaceWith(fragment);
                    }
                });

                if (window.history.replaceState) {
                    window.history.replaceState(
                        {}, document.title, new URI(url).readable()
                    );
                }

                $(document).trigger('fragments-loaded', [loaded_fragments]);
            });
        };

        return {
            'load': self.load
        };
    };

    /*
        Queries the current url with the parameter '&select-[field]=[value]'
        using ajax and goes through the result replacing the
        list-select-fragments on the current page with the ones found in
        the result of the ajax request. Each fragments needs its own id
        for this process to work:

        e.g.

        with this fragment...
        <div class="filter-fragment" id="filter-fragment-1" />

        ...this call...
        $.ListFilter().filter('country', 'CH')

        ..will request...
        http://my-url.com/index?x=1&select-country=CH

        ...and replace the mentioned fragment.
    */
    $.ListFilter = function(options) {

        var self = {};
        var loader = $.FragmentsLoader();

        self.options = $.extend({
            'prefix': 'filter-'
        }, options);

        /*
            gets the current url, removing all traces of
            list selector's own query parameters
        */
        self.build_url = function(fieldmap) {
            var uri = URI(window.location.href);

            // remove the prefixed query arguments
            var params = uri.query(true);
            params = _.omit(params,
                _.filter(_.keys(params), function(key) {
                    return key.indexOf(self.options.prefix) != -1;
                })
            );

            // optionally add the given arguments
            if (! _.isUndefined(fieldmap)) {
                _.each(fieldmap, function(value, key) {

                    // add the prefix if not defined
                    if (key.indexOf(self.options.prefix) == -1) {
                        key = self.options.prefix + key;
                    }

                    params[key] = value;
                });
            }

            // reset the batching
            if (_.has(params, 'b_start:int')) {
                delete params['b_start:int'];
            }

            // reset the letter
            if (_.has(params, 'letter')) {
                delete params['letter'];
            }

            return uri.query(params).toString();
        };

        /*
            filters the table with the given field/value. if either of those
            are undefined, the possibly filtered table is reset.
        */
        self.filter = function(field, value) {
            var fieldmap = {};
            if (!_.isUndefined(field) && !_.isUndefined(value)) {
                fieldmap[field] = value;
            }

            var url = self.build_url(fieldmap);
            self.filter_by_url(url);
        };

        self.filter_by_url = function(url) {
            loader.load(url);
        };

        // public functions
        return {
            'filter': self.filter,
            'filter_by_url': self.filter_by_url
        };
    };

    /*
        Drives the ListFilter through select elements. Each select element
        is expected to have an 'all' value with the value set to '__all__' that
        is supposed to trigger the reset of the filter. The select must also
        have a data-attribute called 'data-filter-attribute' which referes to the
        fieldname used on the ListFilter. The field-name is passed to the
        filter function when the selection changes along with the text of
        the selected option.

        An optional reset-element may be specified which triggers a reset of the
        filter if it is clicked. All options are also passed along to the
        ListFilter.

        Only one selection is ever used - they are not combined.
    */
    $.fn.ListFilterTable = function(options) {
        var table = $(this);

        options = $.extend({
            'reset-element': null,
            'select-elements': 'select'
        }, options);

        var selects = table.find(options['select-elements']);
        var list_filter = $.ListFilter(options);

        var reset_handler = function(e) {
            list_filter.filter();
            selects.find('option[value="__all__"]').attr(
                'selected', 'selected'
            );
            e.preventDefault();
        };

        var handle_fragment_click = function(e) {
            list_filter.filter_by_url($(this).attr('href'));
            window.scrollTo(0, 0);
            e.preventDefault();
        };

        var setup_fragment_handlers = function() {
            if (options['reset-element']) {
                $(options['reset-element']).click(
                    acquire_lock('change-box', reset_handler)
                );
            }
            $('.listingBar a').click(handle_fragment_click);
            $('.people-letters a').click(handle_fragment_click);
        };

        setup_fragment_handlers();
        $(document).on('fragments-loaded', setup_fragment_handlers);

        return selects.each(function() {

            var box = $(this);
            var attribute = box.data('filter-attribute');

            var selected_value = function() {
                var selected = box.find('option:selected');
                if (selected.attr('value') == '__all__') {
                    return null;
                } else {
                    return selected.text();
                }
            };

            var change_handler = function(e) {
                var value = selected_value();

                if (value !== null) {
                    list_filter.filter(attribute, value);
                } else {
                    list_filter.filter();
                }

                _.each(selects, function(other_box) {
                    if (other_box != box.get(0)) {

                        // reset the selection of the other selects to
                        // indicate that the different selections are not
                        // combined together

                        $(other_box).find('option[value="__all__"]').attr(
                            'selected', 'selected'
                        );
                    }
                });
            };

            box.change(acquire_lock('change-box', change_handler));
        });
    };
});