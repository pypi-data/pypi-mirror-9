$(function () {
    if ($('#result_list').length !== 0) {
        var groups            = {},
            $table            = $('#result_list'),
            tbody, rowCounter = 0,
            csrfToken         = $('input[name="csrfmiddlewaretoken"]').val(),
            groupKeys         = [],
            group;

        $('.object-tools')
            .add('.actions')
            .add('.action-checkbox-column')
            .add('.action-checkbox')
            .add('.field-plugin_type')
            .add('.column-plugin_type')
            .add('.field-order')
            .add('.column-order')
            .hide();

        $table.find('tbody tr').each(function () {
            var $this       = $(this),
                pluginType  = $this.find('.field-plugin_type').text(),
                pluginName  = $this.find('.field-__unicode__').text();
                pluginOrder = $this.find('.field-order').text();

            if (!groups[pluginType]) groups[pluginType] = [];

            groups[pluginType].push({
                name:  pluginName,
                order: pluginOrder,
                $elem: $this
            });

            $this.remove();
        });

        groupKeys = Object.keys(groups).sort();

        for (var g = 0; g < groupKeys.length; g +=1) {
            group = groupKeys[g];
        // for (var group in Object.keys(groups).sort()) {
            if (groups.hasOwnProperty(group)) {
                groups[group] = groups[group].sort(function (a, b) {
                    return parseInt(a.order) - parseInt(b.order)
                });

                $tbody = $('<tbody id="group[' + group + ']"></tbody>');
                $tbody.append('<tr><td colspan="2" style="color: #666; font-weight: bold;">' + group + '</td></tr>');

                rowCounter = 0;

                for (var plugin = 0; plugin < groups[group].length; plugin +=1) {
                    groups[group][plugin].$elem.removeClass('row1 row2');
                    groups[group][plugin].$elem.addClass(rowCounter % 2 === 0 ? 'row1' : 'row2');

                    $tbody.append(groups[group][plugin].$elem);

                    rowCounter += 1;
                }

                $tbody.sortable({
                    containment: 'parent',
                    stop: function (event, ui) {
                        var orderCounter = -1,
                            plugins      = [];

                            $tbody.find('.row1, .row2').each(function () {
                                orderCounter += 1;

                                plugins.push({
                                    name:   $(this).find('.field-__unicode__').text().toString(),
                                    order:  orderCounter.toString(),
                                    id    : $(this).find('.action-checkbox input').val()
                                });
                            });

                            $.post(window.update_plugins_order, {
                                data:                JSON.stringify(plugins),
                                csrfmiddlewaretoken: csrfToken
                            })

                            // $.post(window.update_plugins_order, {
                            //     plugins:             plugins,
                            //     csrfmiddlewaretoken: csrfToken
                            // });
                    }
                });

                $table.append($tbody);
            }
        }
    } else {
        CodeMirror.fromTextArea(document.getElementById("id_options"), {
            mode: 'javascript'
        })
    }

});