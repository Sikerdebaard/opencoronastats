// BEGIN DEEPMERGE https://github.com/TehShrike/deepmerge
function isMergeableObject(val) {
    var nonNullObject = val && typeof val === 'object'

    return nonNullObject
        && Object.prototype.toString.call(val) !== '[object RegExp]'
        && Object.prototype.toString.call(val) !== '[object Date]'
}

function emptyTarget(val) {
    return Array.isArray(val) ? [] : {}
}

function cloneIfNecessary(value, optionsArgument) {
    var clone = optionsArgument && optionsArgument.clone === true
    return (clone && isMergeableObject(value)) ? deepmerge(emptyTarget(value), value, optionsArgument) : value
}

function defaultArrayMerge(target, source, optionsArgument) {
    var destination = target.slice()
    source.forEach(function(e, i) {
        if (typeof destination[i] === 'undefined') {
            destination[i] = cloneIfNecessary(e, optionsArgument)
        } else if (isMergeableObject(e)) {
            destination[i] = deepmerge(target[i], e, optionsArgument)
        } else if (target.indexOf(e) === -1) {
            destination.push(cloneIfNecessary(e, optionsArgument))
        }
    })
    return destination
}

function mergeObject(target, source, optionsArgument) {
    var destination = {}
    if (isMergeableObject(target)) {
        Object.keys(target).forEach(function (key) {
            destination[key] = cloneIfNecessary(target[key], optionsArgument)
        })
    }
    Object.keys(source).forEach(function (key) {
        if (!isMergeableObject(source[key]) || !target[key]) {
            destination[key] = cloneIfNecessary(source[key], optionsArgument)
        } else {
            destination[key] = deepmerge(target[key], source[key], optionsArgument)
        }
    })
    return destination
}

function deepmerge(target, source, optionsArgument) {
    var array = Array.isArray(source);
    var options = optionsArgument || { arrayMerge: defaultArrayMerge }
    var arrayMerge = options.arrayMerge || defaultArrayMerge

    if (array) {
        return Array.isArray(target) ? arrayMerge(target, source, optionsArgument) : cloneIfNecessary(source, optionsArgument)
    } else {
        return mergeObject(target, source, optionsArgument)
    }
}

deepmerge.all = function deepmergeAll(array, optionsArgument) {
    if (!Array.isArray(array) || array.length < 2) {
        throw new Error('first argument should be an array with at least two elements')
    }

    // we are sure there are at least 2 values, so it is safe to have no initial value
    return array.reduce(function(prev, next) {
        return deepmerge(prev, next, optionsArgument)
    })
}

// END DEEPMERGE

function filter_zero_vals(arr) {
    return arr.map(function(d) {
        return d == 0 ? null : d
    })
}

function filter_last_three(arr) {
    return arr.slice(0, -3)
}

function last_three(arr) {
    return null_array(arr.length - 4).concat(arr.slice(-4))
}

function get_values_for(data, field) {
    return data.map(function(d) {
        return d[field]
    })
}

function get_column_name_by_index(data, index) {
    return Object.keys(data[0])[index]
}

function to_int(arr) {
    return arr.map(function(d) {
        return Math.floor(d)
    })
}

function append_last_nonzero_value_to_end(arr) {
    arr[arr.length - 1] = arr.filter(function(x) {
        return x != null
    }).slice(-1)[0]
    return arr
}

function percentage_fraction_to_percentage(arr) {
    return arr.map(function(d) {
        return d == null ? null : Math.floor(d * 10000) / 100
    })
}

function remove_last(arr) {
    return arr.slice(0, -1)
}


filter_functions = {
    'filter_zero_values': filter_zero_vals,
    'remove_last_three': filter_last_three,
    'last_three_rest_null' : last_three,
    'to_int': to_int,
    'append_last_nonzero_value_to_end': append_last_nonzero_value_to_end,
    'percentage_fraction_to_percentage': percentage_fraction_to_percentage,
    'remove_last': remove_last
}

function arrayContains(needle, arrhaystack)
{
    return (arrhaystack.indexOf(needle) > -1);
}

function do_filter(dataset, data) {
    if (Array.isArray(dataset['filter'])) {
        var filters = dataset['filter']

        for (var n=0; n < filters.length; n++) {
            data = filter_functions[filters[n]](data)
        }
    } else {
        data = filter_functions[dataset['filter']](data)
    }
    return data
}

function append_datasets_to_template(data, template, options, default_dataset_config={}) {
    var datasets = []
    for (var j = 0; j < options.length; j++) {
        var dataset_configured = {}
        var dataset = options[j]
        var keys = Object.keys(dataset)

        for (var n in keys) {
            key = keys[n]
            if (key == 'column') {
                if (arrayContains('filter', keys)){
                    dataset_configured['data'] = do_filter(dataset, get_values_for(data, dataset[key]))
                } else {
                    dataset_configured['data'] = get_values_for(data, dataset[key])
                }
            } else if(key == 'columnbyindex') {
                if (arrayContains('filter', keys)) {
                    dataset_configured['data'] = do_filter(dataset, get_values_for(data, get_column_name_by_index(data, dataset[key])))
                } else {
                    dataset_configured['data'] = get_values_for(data, get_column_name_by_index(data, dataset[key]))
                }
            } else if(key == 'label') {
                if (dataset[key].trim().startsWith('%') && dataset[key].trim().endsWith('%')) {
                    if (dataset[key].trim() == '%column%') {
                        if (arrayContains('column', keys)) {
                            dataset_configured[key] = dataset['column']
                        } else {
                            dataset_configured[key] = get_column_name_by_index(data, dataset['columnbyindex'])
                        }
                    }
                } else {
                    dataset_configured[key] = dataset[key]
                }
            } else if (arrayContains(key, ['filter'])){
                continue
            } else if (arrayContains(key, ['backgroundColor', 'borderColor'])) {
                dataset_configured[key] = chartconfig['colors'][dataset[key]]
            } else {
                dataset_configured[key] = dataset[key]
            }
        }
        var ds = deepmerge(default_dataset_config, dataset_configured)
        datasets.push(ds)
    }

    template['data']['datasets'] = datasets
    return template
}

function generate_options(chart_info, default_config, default_config2={}) {
    var config = deepmerge(default_config, default_config2)
    if ('options' in chart_info) {
        config = deepmerge(config, chart_info['options'])
        return config
    }
    return config
}

function drawDemographics(chart_info) {
    data = datasets[chart_info['uses']]

    template = append_datasets_to_template(data, {
        type: 'bar',
        data: {
            labels: get_values_for(data, chart_info['x']),
        },
        options: generate_options(chart_info, chartconfig['default_options'], chartconfig['default_demographics_options'])
    }, chart_info['datasets'])

    new Chart(document.getElementById(chart_info['name']), template)
}

function drawLine(chart_info) {
    data = datasets[chart_info['uses']]

    template = append_datasets_to_template(data, {
        type: 'line',
        data: {
            labels: get_values_for(data, chart_info['x']),
        },
        options: generate_options(chart_info, chartconfig['default_options'], chartconfig['default_demographics_options'])
    }, chart_info['datasets'], chartconfig['linechart_default_dataset_vals'])

    new Chart(document.getElementById(chart_info['name']), template)
}


datasets = {}

function download_dataset(dataset) {
    var ts = new Date().getTime()
    if (dataset.endsWith('.json')) {
        return d3.json(dataset + '?' + ts)
    } else {
        return d3.csv(dataset + '?' + ts)
    }
}

function update(){
    //console.log('Updating')

    proms = []
    for (var i in chartdata['datasets']) {
        proms.push(download_dataset(chartdata['datasets'][i]))
    }

    Promise.all(proms).then(function (files) {
        for (var i in chartdata['datasets']) {
            datasets[chartdata['datasets'][i].split(/\.(?=[^\.]+$)/)[0]] = files[i]
        }
        draw()
     })
}

function draw() {
    for (i in chartdata['charts']) {
        var chart = chartdata['charts'][i]
        if (chart['type'] == 'demographics') {
            drawDemographics(chart)
        } else if (chart['type'] == 'line') {
            drawLine(chart)
        }
    }

    for (i in cards) {
        carddata = datasets['cards'][cards[i]]
        document.getElementById(cards[i]).querySelectorAll('*').forEach(function(el) {
            el.className = el.className.replace(/\bgreen\b/g, carddata['color'])
            el.className = el.className.replace(/\bred\b/g, carddata['color'])
        })

        var caret = ''
        if ('trend' in carddata) {
            var trend = carddata['trend']
            if (trend == 0) {
                caret = 'fa-caret-right'
            } else if (trend == 1) {
                caret = 'fa-caret-up'
            } else {
                caret = 'fa-caret-down'
            }
        }

        var el = document.getElementById(cards[i] + '-arrow')
        el.className = el.className.replace(/\bfa-caret-up\b/g, caret)
        el.className = el.className.replace(/\bfa-caret-down\b/g, caret)
        el.className = el.className.replace(/\bfa-caret-right\b/g, caret)

        el = document.getElementById(cards[i] + '-value').innerHTML = carddata['value']
        el = document.getElementById(cards[i] + '-title').innerHTML = carddata['title']
    }
}

function updateTimestamp(data){
    var isoDateTime = new Date(data)
    document.getElementById('last-update').innerHTML = isoDateTime.toLocaleDateString('nl-NL') + " " + isoDateTime.toLocaleTimeString('nl-NL')
}

function null_array(length) {
    var out = []

    while (out.length < length) {
        out.push(null)
    }

    return out
}

update()
setInterval(function () {
    update()
}, 600 * 3000) // update every 30 min
