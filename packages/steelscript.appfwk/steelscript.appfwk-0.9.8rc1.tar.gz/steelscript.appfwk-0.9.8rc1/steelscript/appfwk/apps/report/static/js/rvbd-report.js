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
 * Stores all methods connected to rendering reports and embedded widgets,
 * as well as all state for the current report/embedded widget display.
 */
rvbd.report = {
    widgets: [],
    debug: false,

    runRequested: false,
    debugFlag: false,
    launchingPrintWindow: false,

    reportHasRendered: false,

    /**
     * Called after DOM load to set up and launch report (or embedded widget).
     */
    start: function() {
        $.ajaxSetup({
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', rvbd.report.csrfToken);
                xhr.setRequestHeader('X-AuthToken', rvbd.report.authToken);
            }
        });

        if (rvbd.report.isEmbedded) { // We already have the widget spec data, so launch right away
            rvbd.report.runFixedCriteriaReport();
        } else if (rvbd.report.reloadMinutes > 0) { // Auto-run report (updates at intervals)
            rvbd.report.runFixedCriteriaReport();
            setInterval(rvbd.report.runFixedCriteriaReport, rvbd.report.reloadMinutes * 60 * 1000);
        } else if (typeof rvbd.report.printCriteria !== 'undefined') { // We're in print view, so launch right away
            rvbd.report.doRunFormReport(false);
        } else { // Standard report
            var $form = $('#criteria-form');

            $form.submit(function() {
                // If not launching print window, run report. If launching print window,
                // allow standard POST request.
                if (!rvbd.report.launchingPrintWindow) {
                    rvbd.report.runFormReport();
                    return false;
                }
            });

            // Attach handlers for "Run" button/menu
            $('#button-run').click(function() { $form.submit(); });

            $('#menu-debug').click(function() {
                    rvbd.report.debugFlag = true;
                    $form.submit();
            });
            $('#menu-update-time-run').click(function() {
                $('#timenow_endtime_1, #datenow_endtime_1').click();
                $form.submit();
            });
            $('#menu-run').click(function() { $form.submit(); });

            $("#criteria").on('hidden', rvbd.report.doRunFormReport);
        }
    },

    /**
     * Launches print view in new window. If there are oversized tables, prompts
     * the user to see if they want to have them expanded in the final output.
     */
    launchPrintWindow: function() {
        function doLaunch(expandTables) {
            var $form = $('#criteria-form');
            var origAction = $form.attr('action');

            $form.attr('action', origAction + 'print/');

            $('#id_expand_tables').val(expandTables ? 'on' : '');

            // The submit handler on the criteria form checks launchingPrintWindow
            // and allows a standard POST submit if it's true.
            rvbd.report.launchingPrintWindow = true;
            $form.submit();
            rvbd.report.launchingPrintWindow = false;

            $form.attr('action', origAction);
        }

        var oversizedTablesFound = false;
        $.each(rvbd.report.widgets, function(i, widget) {
            if (widget.isOversized()) {
                oversizedTablesFound = true;
            }
        });

        if (oversizedTablesFound) {
            var okCallback = function() { doLaunch(true); },
                cancelCallback = function() { doLaunch(false); },
                content = "Some table(s) contain too much content to fit at standard height " +
                          "and will be cut off. Would you like to extend these tables vertically " +
                          "to show all data?";
            rvbd.modal.confirm("Print report", content, "Don't extend", "Extend", okCallback, cancelCallback);
        } else {
            doLaunch(false);
        }
    },

    /**
     * Launch a report based on fixed criteria (i.e. auto-run or embedded widget).
     */
    runFixedCriteriaReport: function() {
        $.ajax({
            dataType: 'json',
            type: 'get',
            url: rvbd.report.widgetsUrl,
            success: function(data, textStatus, jqXHR) {
                rvbd.report.renderWidgets(data);
            },
            error: function(jqXHR, textStatus, errorThrown) { 
                rvbd.report.alertReportError(textStatus, errorThrown);
            }
        });
    },

    /**
     * Called when user chooses new criteria through UI
     */
    criteriaChanged: function() {
        $('body').css('cursor', 'wait');

        rvbd.report.form = $('#criteria-form');
        rvbd.report.form.ajaxSubmit({
            dataType: 'json',
            type: 'post',
            url: rvbd.report.form.attr('action') + 'criteria/',
            complete: function(data, textStatus, jqXHR) {
                $('body').css('cursor', 'default');
            },
            success: function(data, textStatus) {
                rvbd.report.updateCriteria(data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.status === 400) { // Form validation problems
                    $('#criteria').collapse('show');
                    $('#form-error-info').html(jqXHR.responseText);
                } else {
                    rvbd.report.alertReportError(textStatus, errorThrown);
                }
            }
        });
    },

    enablePrintButton: function() {
        $('<a id="print-report" class="icon-print" href="#" title="Print this report"></a>')
             .click(rvbd.report.launchPrintWindow)
             .replaceAll('#print-report');
    },

    disablePrintButton: function() {
        $('<span id="print-report" class="icon-print" title="Print this report (run report to enable)"></span>')
             .replaceAll('#print-report');
    },

    /** 
     * Starts execution of a standard form-based report; not used for embedded widgets or auto-run
     * reports. rvbd.report.doRunStandardReport() is triggered after the criteria box is fully collapsed.
     */
    runFormReport: function() {
        rvbd.report.runRequested = true;
        $("#criteria").collapse('hide'); // self.doRunReport() triggers on this element being hidden
    },

    /**
     * Performs the actual execution of a standard report (runFormReport updates the UI and then
     * runs this).
     */
    doRunFormReport: function(checkRunRequested) {
        if (typeof checkRunRequested === 'undefined' || checkRunRequested) {
            // Avoid accidental double clicks -- if this has already been executed since the last time
            // the user requested to run the report, abort.
            if (!rvbd.report.runRequested) {
                return;
            }

            rvbd.report.runRequested = false;
        }

        var $form = $('#criteria-form'),
            ajaxParams = {
                dataType: 'json',
                type: 'post',
                url: $form.attr('action'),
                complete: function(jqXHR, textStatus) {
                    $('body').css('cursor', 'default');
                },
                success: function(data, textStatus) {
                    rvbd.report.renderWidgets(data);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    if (jqXHR.status === 400) {
                        $('#criteria').collapse('show');
                        $('#form-error-info').html(jqXHR.responseText);
                    } else {
                        rvbd.report.alertReportError(textStatus, errorThrown);
                    }
                }
            };

        if (typeof rvbd.report.printCriteria !== 'undefined') { // Print view
            ajaxParams.data = rvbd.report.printCriteria;
            $.ajax(ajaxParams);
        } else { // Standard form submit
            $form.ajaxSubmit(ajaxParams);
        }

        $('#id_debug').val(rvbd.report.debugFlag ? 'on' : '');
        $('#form-error-info').empty();
        $('body').css('cursor', 'wait');

        rvbd.report.debugFlag = false;
    },

    /*
     * Called to update criteria field HTML after the user chooses new criteria.
     */
    updateCriteria: function(data) {
        $.each(data, function(i, w) {
            $('#' + w.id + '-span').html(w.html);
        });
    },

    /**
     * Call to alert the user when we receive a server error from a report-wide
     * problem (e.g., invalid criteria).
     */
    alertReportError: function(textStatus, errorThrown) {
        alert("An error occurred: " + textStatus + ": " + errorThrown)
    },

    /**
     * Renders all widgets in the current report (or just the one if this is an
     * embedded widget).
     */
    renderWidgets: function(widgets) {
        var $report = $('#report'),
            reportMeta = widgets.shift(), // pull first element off list which contains information about the report
            widgetsToRender;

        $('#id_debug').val(rvbd.report.debugFlag ? 'on' : '');
        rvbd.report.debug = reportMeta.debug;

        $('#report-datetime').html(reportMeta.datetime);
        $('#report-timezone').html(reportMeta.timezone);

        $report.empty();

        if (!rvbd.report.isEmbedded) { // Full report
            widgetsToRender = widgets;
        } else { // Embedded widget
            // Find the widget we want to render
            var targetWidget;
            $.each(widgets, function(i, widget) {
                if (widget.widgetslug === rvbd.report.embedWidgetInfo.widgetslug) {
                    targetWidget = widget;
                    return false;
                }
            });

            // Replace the default criteria with the criteria from the widget request URL.
            $.extend(targetWidget.criteria, rvbd.report.embedWidgetInfo);

            widgetsToRender = [targetWidget];
        }

        // Clear existing list of widgets
        rvbd.report.widgets = [];

        var $row,
            rownum = 0,
            opts,
            widget;
        $.each(widgetsToRender, function(i, w) {
            if (w.row !== rownum) { // If we're at a new row number, create a new row element
                $row = $('<div></div>')
                    .addClass('row-fluid')
                rownum = w.row;
            }

            // Create empty div that the new widget object will populate
            var $div = $('<div></div>')
                .appendTo($row);
            $report.append($row);

            opts = w.options || {};
            opts.height = w.height;
            opts.width = w.width;

            var widgetModule = w.widgettype[0],
                widgetClass = w.widgettype[1];

            widget = new rvbd.widgets[widgetModule][widgetClass](w.posturl, rvbd.report.isEmbedded, $div[0],
                                                                 w.widgetid, w.widgetslug, opts, w.criteria);
            rvbd.report.widgets.push(widget);
        });

        if (!rvbd.report.reportHasRendered) { // If first time rendering the report, attach widgetDoneLoading handler
            rvbd.report.reportHasRendered = true;

            $(document).on('widgetDoneLoading', function(e, widget) {
                rvbd.report.handleReportLoadedIfNeeded();
            });
        }
    },

    /**
     * Check if all widgets are done loading, and if so, update the UI to indicate
     * the report is loaded.
     */
    handleReportLoadedIfNeeded: function() {
        var widgetsRunning = false;
        $.each(rvbd.report.widgets, function(i, widget) {
            if (widget.status === 'running') {
                widgetsRunning = true;
                return;
            }
        });

        if (!widgetsRunning) {
            if (rvbd.report.debug) {
                rvbd.modal.alert("Download Zip File",
                                 "Complete - you will now be prompted to download a " +
                                 "zipfile containing the server logs.", "OK",
                                 function() { window.location = rvbd.report.debugUrl; });
            }

            rvbd.report.enablePrintButton();
        }
    }
};

})();
