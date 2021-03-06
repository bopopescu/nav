require(['plugins/graphfetcher', 'libs/jquery'], function (GraphFetcher) {
    /*
     * This plugin will provide global controls to the graphs if
     * you wrap your graphs in an element with class 'nav-metrics-container'
     * and provide some more elements.
     *
     * Example:
     * <div class='nav-metrics-container'>
     *   <div class="graphitegraph" data-url="{% url interface-counter-graph port.id 'Octets' %}"></div>
     *   <div class="graphitegraph" data-url="{% url interface-counter-graph port.id 'Octets' %}"></div>
     * </div>
     *
     * You can create buttons inside 'nav-metrics-controller' to open and
     * close all graphs. These need the class 'all-graph-opener' and
     * 'all-graph-closer' respectively.
     *
     * If you provide an element with the class 'all-graph-buttons', it will
     * be populated with buttons for choosing timeframe for all graphs
     */

    function addToggleListeners($parent, graphs) {
        /* Add listeners for opening and closing all graphs */
        $parent.find('.all-graph-opener').click(function () {
            for (var i = 0, l = graphs.length; i < l; i++) {
                graphs[i].open();
            }
        });
        $parent.find('.all-graph-closer').click(function () {
            for (var i = 0, l = graphs.length; i < l; i++) {
                graphs[i].close();
            }
        });
    }

    function addGraphUrlSwitcher($parent, graphs) {
        /* Switch graph url index based on graph-switcher index */
        $parent.find('.all-graph-url-switcher').each(function () {
            var $switchers = $(this).find('.graph-switcher');
            $switchers.each(function (index, element) {
                if (index === 0) {
                    $(element).addClass('active');
                }
                $(element).click(function () {
                    $switchers.removeClass('active');
                    $(this).addClass('active');
                    for (var i = 0, l = graphs.length; i < l; i++) {
                        graphs[i].changeUrlIndex(index);
                        if (graphs[i].isOpen) {
                            graphs[i].loadGraph();
                        }
                    }
                });
            });
        });
    }

    function addTimeframeSwitcher($parent, graphs) {
        /* Add buttons for choosing timeframe for all graphs */
        $parent.find('.all-graph-buttons').each(function () {
            var buttons = graphs[0].buttons, // We assume at least one graph
                $container = $(this), first = true;

            for (var key in buttons) {
                if (buttons.hasOwnProperty(key)) {
                    var button = $('<button>').addClass('tiny secondary graph-button-' + key).html(buttons[key]).appendTo(this);
                    if (first) {
                        button.addClass('active');
                        first = false;
                    }
                }
            }
            $container.on('click', 'button', function (event) {
                var $button = $(event.target), buttonClass = $button.attr('class'), timeframe = buttonClass.match(/graph-button-[a-z]+/)[0].split('-')[2];
                for (var i = 0, l = graphs.length; i < l; i++) {
                    graphs[i].timeframe = timeframe;
                    if (graphs[i].isOpen) {
                        graphs[i].loadGraph();
                    }
                }
                $container.find('button').removeClass('active');
                $button.addClass('active');
            });
        });
    }

    $(function () {
        $('.nav-metrics-container').each(function (index, element) {
            var $parent = $(element),
                graphs = [];

            /* Create all graphs and store them */
            $parent.find('.graphitegraph').each(function () {
                var $node = $(this);
                try {
                    graphs.push(new GraphFetcher($node, $node.attr('data-url')));
                } catch (error) {
                    console.log('Error initializing graphloader');
                }
            });

            if (graphs.length > 0) {
                addToggleListeners($parent, graphs);
                addGraphUrlSwitcher($parent, graphs);
                addTimeframeSwitcher($parent, graphs);
            }

        });
    });

});
