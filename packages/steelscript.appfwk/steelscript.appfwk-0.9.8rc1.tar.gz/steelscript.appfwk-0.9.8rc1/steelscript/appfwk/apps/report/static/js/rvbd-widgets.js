/**
 # Copyright (c) 2013 Riverbed Technology, Inc.
 #
 # This software is licensed under the terms and conditions of the
 # MIT License set forth at:
 #   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
 # This software is distributed "AS IS" as set forth in the License.
 */

(function() {
'use strict';

/**
 * Utility funcs for formatting numbers and times. Called on every data point 
 * in raw widget data to pre-format the values for the JS lib (or just to make
 * them look nicer to for the end user). Server-side code decides which of
 * these gets called to process the data for a given widget.
 */
rvbd.formatters = {
    padZeros: function(n, p) {
        var pad = (new Array(1 + p)).join("0");
        return (pad + n).slice(-pad.length);
    },

    roundAndPadRight: function(num, totalPlaces, precision) {
        var digits = Math.floor(num).toString().length;
        if (typeof precision === 'undefined') {
            if (digits >= totalPlaces) { // Always at least 1 digit of precision
                precision = 1;
            } else { // Include enough precision digits to get the total we want
                precision = (totalPlaces + 1) - digits; // One extra for decimal point
            }
        }
        return num.toFixed(precision);
    },

    formatTime: function(t, precision) {
        return (new Date(t)).toString();
    },

    formatTimeMs: function(t, precision) {
        var d = new Date(t);
        return d.getHours() +
            ':' + rvbd.formatters.padZeros(d.getMinutes(), 2) +
            ':' + rvbd.formatters.padZeros(d.getSeconds(), 2) +
            '.' + rvbd.formatters.padZeros(d.getMilliseconds(), 3);
     },

     formatMetric: function(num, precision) {
        if (typeof num === 'undefined') { 
            return "";
        } else if (num === 0) {
            return "0";
        }

        num = Math.abs(num);

        var e = parseInt(Math.floor(Math.log(num) / Math.log(1000))),
            v = (num / Math.pow(1000, e));

        var vs = rvbd.formatters.roundAndPadRight(v, 4, precision);

        if (e >= 0) {
            return vs + ['', 'k', 'M', 'G', 'T'][e];
        } else {
            return vs + ['', 'm', 'u', 'n'][-e];
        }
    },

    formatIntegerMetric: function(num, precision) {
        return rvbd.formatters.formatMetric(num, 0);
    },

    formatPct: function(num, precision) {
        if (typeof num === 'undefined') {
            return "";
        } else if (num === 0) {
            return "0";
        } else {
            return rvbd.formatters.roundAndPadRight(num, 4, precision)
        }
    }
};

rvbd.widgets = {};

rvbd.widgets.Widget = function(postUrl, isEmbedded, div, id, slug, options, criteria) {
    var self = this;

    self.postUrl = postUrl;
    self.div = div;
    self.id = id;
    self.slug = slug;
    self.options = options;
    self.criteria = criteria;

    self.status = 'running';

    var $div = $(div);

    $div.attr('id', 'chart_' + id)
        .addClass('widget blackbox span' + (isEmbedded ? '12' : options.width))
        .text("Widget " + id);

    if (options.height) {
        $div.height(options.height);
    }

    $div.html("<p>Loading...</p>")
        .showLoading()
        .setLoading(0);

    $.ajax({
        dataType: 'json',
        type: 'POST',
        url: self.postUrl,
        data: { criteria: JSON.stringify(criteria) },
        success: function(data, textStatus) {
            self.jobUrl = data.joburl;
            setTimeout(function() { self.getData(criteria); }, 1000);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var message = $("<div/>").html(textStatus + " : " + errorThrown).text()
            $div.hideLoading()
                .append("<p>Server error: <pre>" + message + "</pre></p>");
            self.status = 'error';
        }
    });
};

rvbd.widgets.Widget.prototype = {
    getData: function(criteria) {
        var self = this;

        $.ajax({
            dataType: "json",
            url: self.jobUrl,
            data: null,
            success: function(data, textStatus) {
                self.processResponse(criteria, data, textStatus);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                self.displayError(errorThrown);
            }
        });
    },

    processResponse: function(criteria, response, textStatus) {
        var self = this;

        switch (response.status) {
            case 3: // Complete
                $(self.div).hideLoading();
                self.render(response.data);
                self.status = 'complete';
                $(document).trigger('widgetDoneLoading', [self]);
                break;
            case 4: // Error
                self.displayError(response);
                self.status = 'error';
                $(document).trigger('widgetDoneLoading', [self]);
                break;
            default:
                $(self.div).setLoading(response.progress);
                setTimeout(function() { self.getData(criteria); }, 1000);
        }
    },

    /** 
     *  Take the raw JSON object returned from the server and generate HTML to
     *  fill the widget DIV.
     */
    render: function(data) {
        var self = this;

        $(self.div).html(data);
    },

    /**
     * Returns a boolean indicating if the widget's content is too big for it
     * (i.e. it's scrolling). If so it will need to be enlarged in print view
     * if the user chooses "Expand Tables."
     */
    isOversized: function() {
        return false;
    },

    /**
     * Takes a JSON response object from a widget that failed with an error;
     * populates the widget with an error message based on the response.
     */
    displayError: function(response) {
        var self = this;

        var isException = (response.exception !== ''),
            $shortMessage = $('<span></span>').addClass('short-error-text'),
            $div = $(self.div);

        if (isException) { // Python exceptions are always text (encoded as HTML)
            $shortMessage.html(response.message);
        } else { // Non-exception errors sometimes contain HTML (double-encoded, e.g. <hr> becomes &lt;hr&gt;)
            $shortMessage.html($('<span></span>').html(response.message).text());
        }

        var $error = $('<div></div>')
            .addClass('widget-error')
            .append("Internal server error:<br>")
            .append($shortMessage)

        if (isException) {
            $error.append('<br>')
                  .append($('<a href="#">Details</a>')
                       .click(function() { self.launchTracebackDialog(response); }));
        }

        $div.hideLoading();

        $div.empty()
            .append($error);

        self.status = 'error';
    },

    launchTracebackDialog: function(response) {
        rvbd.modal.alert("Full Traceback", "<pre>" + $('<div></div>').text(response.exception).html() + "</pre>",
                         "OK", function() { }, 'widget-error-modal');
    },

    /**
     * Adds menu chevron to widget title bar
     */
    addMenu: function() {
        var self = this;

        var menuItems = [
            '<a tabindex="-1" class="get-embed" href="#">Embed This Widget...</a>',
            '<a tabindex="0" id="' + self.id + '_export_widget_csv" class="export_widget_csv" href="#">Export CSV (Table Data)...</a>'
        ];

        var $menuContainer = $('<div></div>')
                .attr('id', 'reports-dropdown')
                .addClass('dropdown'),
            $menuButton = $('<a></a>')
                .attr('id', self.id + '_menu')
                .addClass('dropdown-toggle widget-dropdown-toggle')
                .attr({
                    href: '#',
                    'data-toggle': 'dropdown'
                }),
            $menuIcon = $('<span></span>')
                .addClass('icon-chevron-down'),
            $menu = $('<ul></ul>')
                .addClass('dropdown-menu widget-dropdown-menu')
                .attr({
                    role: 'menu',
                    'aria-labelledby': self.id + '_menu'
                });

        // Add each menu item to the menu
        $.each(menuItems, function(i, menuItem) {
            $('<li></li>').attr('role', 'presentation')
                          .html(menuItem)
                          .appendTo($menu);
        });

        // Append the menu and the button to our menu container, then add the menu
        // to the widget.
        $menuButton.append($menuIcon);
        $menuContainer.append($menuButton)
                      .append($menu)
                      .appendTo($(self.title));

        $menuContainer.find('.export_widget_csv').click($.proxy(self.onCsvExport, self));

        $(self.title).find('.get-embed').click($.proxy(self.embedModal, self));
    },

    onCsvExport: function() {
        var self = this;

        $.ajax({
            dataType: 'json',
            type: 'POST',
            url: self.postUrl,
            data: { criteria: JSON.stringify(self.criteria) },
            success: function(data, textStatus, jqXHR) {
                self.checkCsvExportStatus(data.joburl);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var alertBody = ("The server returned the following HTTP error: <pre>" +
                                 + errorThrown + '</pre>');
                rvbd.modal.alert("CSV Export Error", alertBody, "OK", function() { })
            }
        });
    },

    checkCsvExportStatus: function(csvJobUrl) {
        var self = this;

        $.ajax({
            dataType: "json",
            url: csvJobUrl + 'status/',
            data: null,
            success: function(data, textStatus) {
                switch (data.status) {
                    case 3: // Complete
                        var origin = window.location.protocol + '//' + window.location.host;
                        // remove spaces and special chars from widget title
                        var fname = self.titleMsg.replace(/\W/g, '');
                        // Should trigger file download
                        window.location = origin + '/data/jobs/' + data.id + '/data/csv/?filename=' + fname;
                        break;
                    case 4: // Error
                        var alertBody = ('The server returned the following error: <pre>' +
                                         data['message'] + '</pre>');
                        rvbd.modal.alert("CSV Export Error", alertBody, "OK", function() { });
                        break;
                    default: // Loading
                        setTimeout(function() { self.checkCsvExportStatus(csvJobUrl); }, 200);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error when checking csv status');

                var alertBody = ('The server returned the following HTTP error: <pre>' + textStatus +
                                 ': ' + errorThrown + '</pre>');
                rvbd.modal.alert("CSV Export Error", alertBody, "OK", function() { });
            }
        });
    },


    /**
     * Construct this widget's basic layout--outer container, title bar, content
     * section. The subclasses are responsible for filling up the content section
     * with widget-specific content.
     */
    buildInnerLayout: function() {
        var self = this;

        var $div = $(self.div);

        self.outerContainer = $('<div></div>')
            .addClass('wid-outer-container')[0];

        self.title = $('<div></div>')
            .attr('id', $div.attr('id') + '_content-title')
            .html(self.titleMsg)
            .addClass('widget-title wid-title')
            .appendTo($(self.outerContainer))[0];

        self.content = $('<div></div>')
            .attr('id', $div.attr('id') + '_content')
            .addClass('wid-content')
            .appendTo($(self.outerContainer))[0];

        self.addMenu();

        $div.empty()
            .append(self.outerContainer);
    },

    /**
     * Display "embed widget" dialog for this widget.
     */
    embedModal: function() {
        var self = this;

        var urlCriteria = $.extend({}, self.criteria);

        // Delete starttime and endtime from params if present (we don't want embedded
        // widgets with fixed time frames)
        delete urlCriteria.starttime;
        delete urlCriteria.endtime;

        var baseUrl = window.location.href.split('#')[0] + 'widgets/'; // Current URL minus anchor
        var url = baseUrl + self.slug + '/render/?';

        //call server for auth token
        $.ajax({
            dataType: 'json',
            type: 'POST',
            url: baseUrl + self.slug + '/authtoken/',
            data: { criteria: JSON.stringify(urlCriteria) },
            success: function(data, textStatus) {
                   self.genEmbedWindow(url, data.auth);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var alertBody = ("The server returned the following HTTP error: <pre>" +
                                 + errorThrown + '</pre>');
                rvbd.modal.alert("Auth Token Generation Error", alertBody, "OK", function() { })
            }
        });
        

    },

    genEmbedWindow: function(url, token) {

        var self = this;
        var authUrl = url + 'auth=' + token;

        /* Generates the source code for the embed iframe */
        function genEmbedCode(url, width, height) {
            return '<iframe width="'+ width + '" height="' + height +
                   '" src="' + url + '" frameborder="0"></iframe>';
        };

        var embedCode = genEmbedCode(authUrl, 500, self.options.height + 12);

        $('#embed-modal #embed-widget-code').attr('value', embedCode);

        rvbd.modal.alert("Embed Widget HTML", $('#embed-modal')[0], "OK", function() {
            // automatically focus and select the embed code
            $('#embed-widget-code')
                .on('mouseup focus', function() { this.select(); })
                .focus();

            // update the embed code to reflect the width and height fields
            $('#widget-width, #widget-height').keyup(function() {
                $('#embed-widget-code').attr('value',
                    genEmbedCode(authUrl, $('#embed-widget-width').val(),
                                          $('#embed-widget-height').val()));
            });
        });
    },
};

rvbd.widgets.raw = {};

rvbd.widgets.raw.TableWidget = function(postUrl, isEmbedded, div, id, slug, options, criteria) {
    rvbd.widgets.Widget.apply(this, [postUrl, isEmbedded, div, id, slug, options, criteria]);
};
rvbd.widgets.raw.TableWidget.prototype = Object.create(rvbd.widgets.Widget.prototype);

rvbd.widgets.raw.TableWidget.prototype.render = function(data) {
    var self = this;

    var $table = $('<table></table>')
                     .attr('id', $(self.div).attr('id') + "_content")
                     .width('100%'),
        $tr;

    $.each(data, function(i, row) {
        $tr = $('<tr></tr>');
        $.each(row, function(i, col) {
            $tr.append('<td></td>').html(col);
        });
        $table.append($tr);
    });

    $(self.div).empty().append($table);
};

})();
