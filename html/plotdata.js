function filter_zero_vals(arr) {
    return arr.map(function(d) {
        return d == 0 ? null : d
    })
}

function get_values_for(data, field) {
    return data.map(function(d) {
        return d[field]
    })
}

filter_functions = {
    'filter_zero_vals': filter_zero_vals
}

default_aesthetics_for_dataset = {
    lineTension: 0.1,
    pointRadius: 5,
    pointHoverRadius: 5
}

default_chart_options = {
    scales: {
        yAxes: [{
            scaleLabel: {
                display: true,
            }
        }]
    },
    tooltips:  {
        mode: 'x',
        bodyFontSize: 14
    },
    animation: {
        duration: 0
    },
    maintainAspectRatio: false
}

colors = {
    patient: "rgba(75, 192, 192, 1)",
    deaths: "rgba(192, 75, 75, 1)",
    recovered: "rgba(75, 192, 75, 1)"
}

charts = {
    demographics: {
        'icu-demographics': {
            x: 'age_group',
            datasets: [{
                label: "Demographics of patients in ICU",
                column: 'all_patients',
                backgroundColor: colors['patient'],
                borderColor: colors['patient'],
                filter: filter_zero_vals,
                scalelabel: 'percentage of patients'
            }]
        },
        'icu-demographics-death': {
            x: 'age_group',
            datasets: [{
                label: "Demographics of deaths in ICU",
                column: 'died',
                backgroundColor: colors['deaths'],
                borderColor: colors['deaths'],
                filter: filter_zero_vals,
                scalelabel: 'percentage of patients'
            }]
        },
        'icu-demographics-recovered': {
            x: 'age_group',
            datasets: [{
                label: "Demographics of recovered patients from ICU",
                column: 'survived',
                backgroundColor: colors['recovered'],
                borderColor: colors['recovered'],
                filter: filter_zero_vals,
                scalelabel: 'percentage of patients'
            }]
        }
    }
}

function append_datasets_to_template(data, template, options) {
    var datasets = []
    for (var j = 0; j < options.length; j++) {
        var dataset_configured = {}
        var dataset = options[j]
        var keys = Object.keys(dataset)

        for (var n in keys) {
            key = keys[n]
            if (key == 'column') {
                if ('filter' in keys){
                    dataset_configured['data'] = dataset['filter'](get_values_for(data, dataset['column']))
                } else {
                    dataset_configured['data'] = get_values_for(data, dataset['column'])
                }
            } else if (key in ['filter']){
                continue
            } else {
                dataset_configured[key] = dataset[key]
            }
        }
        datasets.push(dataset_configured)
    }

    template['data']['datasets'] = datasets
    return template
}

function makeDemographics(data) {
    gen_charts = charts['demographics']

    for (var chart_key in gen_charts) {
        if (!gen_charts.hasOwnProperty(chart_key)) {
            continue
        }
        chart_info = gen_charts[chart_key]
        template = append_datasets_to_template(data, {
            type: 'bar',
            data: {
                labels: get_values_for(data, chart_info['x']),
            },
            options: default_chart_options
        }, chart_info['datasets'])

        new Chart(document.getElementById(chart_key), template)
    }
}




function update(){
    console.log('Updating')
    var ts = new Date().getTime()
    //d3.csv('data.csv?' + ts).then(makeCharts)
    d3.csv('demographics.csv?' + ts).then(makeDemographics)
    //d3.csv('mortality_displacement.csv?' + ts).then(makeMortalityDisplacement)
    d3.json('timestamp.json?' + ts).then(updateTimestamp)
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

//function makeMortalityDisplacement(data) {
//    var headerNames = d3.keys(data[0])
//
//    var xlabels = data.map(function (d) {
//        return d.week
//    })
//
//    var ci_high = data.map(function (d) {
//        return d['ci_0.95_high']
//    })
//
//    var ci_low = data.map(function (d) {
//        return d['ci_0.95_low']
//    })
//
//    var year_header_cols = []
//    var mortality_displacement = {}
//
//    for (var i = 0; i < headerNames.length; i++) {
//        d = headerNames[i]
//        if (d != 'week' & d != 'ci_0.95_low' & d != 'ci_0.95_high') {
//            year_header_cols.push(d)
//            mortality_displacement[d] = data.map(function (r) {
//                return r[d] != "" ? r[d] : null
//            })
//        }
//    }
//
//    colors = [
//        "rgba(192, 75, 192, .2)",
//        "rgba(192, 75, 192, .3)",
//        "rgba(192, 75, 192, .4)",
//        "rgba(192, 75, 192, .5)",
//        "rgba(192, 75, 192, 1)"
//    ]
//
//    datasets = []
//
//    ci_color = "rgba(75, 192, 75, .1)"
//    datasets.push(
//        {
//            label: 'Confidence interval 95% top',
//            data: ci_high,
//            fill: false,
//            backgroundColor: ci_color,
//            borderColor: "transparent",
//            lineTension: 0,
//            pointRadius: 0
//        }
//    )
//    datasets.push(
//        {
//            label: 'Confidence interval 95% bottom',
//            data: ci_low,
//            fill: 0,
//            backgroundColor: ci_color,
//            borderColor: "transparent",
//            lineTension: 0,
//            pointRadius: 0
//        }
//    )
//
//    for (var i = 0; i < year_header_cols.length; i++) {
//        datasets.push(
//            {
//                label: year_header_cols[i],
//                data: mortality_displacement[year_header_cols[i]],
//                fill: false,
//                backgroundColor: colors[i],
//                borderColor: colors[i],
//                lineTension: 0.1,
//                pointRadius: i != 4 ? 0 : 3,
//                pointHoverRadius: i != 4 ? 0 : 10
//            }
//        )
//    }
//
//    var mortality_displacement_chart = new Chart(document.getElementById("mortality-displacement-nl"), {
//        type: 'line',
//        data: {
//            labels: xlabels,
//            datasets: datasets
//        },
//        options: {
//            scales: {
//                yAxes: [{
//                    scaleLabel: {
//                        display: true,
//                        labelString: 'number of deceased'
//                    }
//                }]
//            },
//            animation: animations_config,
//            tooltips: tooltip_config,
//            maintainAspectRatio: false
//        }
//    })
//
//}



//function makeCharts(data) {
//    var headerNames = d3.keys(data[0])
//    var xlabels = data.map(function (d) {
//        return d.date
//    })
//
//    var patients_in_icu = data.map(function (d) {
//        return d.intakeCount
//    })
//
//    var latest_non_null = null
//    var beds_for_covid = data.map(function (d) {
//        var out = d.beds != '' ? d.beds - 500 : null
//        latest_non_null = out != null ? out : latest_non_null
//        return out
//    })
//    beds_for_covid[beds_for_covid.length - 1] = latest_non_null
//
//    var beds = data.map(function (d) {
//        var out = d.beds != '' ? d.beds: null
//        latest_non_null = out != null ? out : latest_non_null
//        return out
//    })
//    beds[beds.length - 1] = latest_non_null
//
//
//    var patients_in_icu_newest = patients_in_icu[patients_in_icu.length - 5]
//    var patients_in_icu_prev = patients_in_icu[patients_in_icu.length - 4]
//
//    document.getElementById('beds-taken-icu').innerText = patients_in_icu_newest
//
//    var growth = data.map(function (d) {
//        return Math.round(d.growth_intakeCount * 10000) / 100
//    })
//
//    var growth_sma5 = data.map(function (d) {
//        return Math.round(d.sma5_growth_intakeCount * 10000) / 100
//    })
//    growth_sma5 = growth_sma5.slice(0, -3)
//
//    var mortality_rate = data.map(function(d) {
//        return d.mortality_rate != '' ? Math.round(d.mortality_rate * 100) : null
//    })
//
//    var last_mortality_rate = mortality_rate[mortality_rate.length - 4]
//    var prev_mortality_rate = mortality_rate[mortality_rate.length - 5]
//    document.getElementById('mortality-in-icu').innerText = last_mortality_rate
//
//    if (last_mortality_rate == prev_mortality_rate) {
//        var color = 'gray'
//        document.getElementById('mortality-arrow').className = 'fas fa-balance-scale'
//    } else if (last_mortality_rate > prev_mortality_rate) {
//        var color = 'red'
//        document.getElementById('mortality-arrow').className = 'fas fa-caret-up'
//    } else {
//        var color = 'green'
//        document.getElementById('mortality-arrow').className = 'fas fa-caret-down'
//    }
//
//    var els = document.getElementsByClassName('mortality-colors')
//    Array.prototype.forEach.call(els, function(el) {
//        el.className = el.className.replace(/\bgreen\b/g, color)
//        el.className = el.className.replace(/\bred\b/g, color)
//        el.className = el.className.replace(/\bgray\b/g, color)
//    })
//
//    var recovered = data.map(function(d) {
//        return d.survivors != '' ? d.survivors : null
//    })
//
//    document.getElementById('patients-recovered-icu').innerText = recovered[recovered.length -1]
//
//    var deaths = data.map(function(d) {
//        return d.died != '' ? d.died : null
//    })
//
//    document.getElementById('patients-died-icu').innerText = deaths[deaths.length - 1]
//
//    var growth_trend = Math.round(data[data.length - 4].sma5_growth_intakeCount * 10000) / 100
//    var growth_trend_prev = Math.round(data[data.length - 5].sma5_growth_intakeCount * 10000) / 100
//    document.getElementById('growth-trend').innerHTML = growth_trend
//
//    var els = document.getElementsByClassName('red-green-swap')
//
//    if (growth_trend_prev > growth_trend) {
//        var newcolor = 'green'
//        var el = document.getElementById('growth-trend-arrow')
//        el.className = el.className.replace(/\bfa-caret-up\b/g, 'fa-caret-down')
//    } else {
//        var newcolor = 'red'
//        var el = document.getElementById('growth-trend-arrow')
//        el.className = el.className.replace(/\bfa-caret-down\b/g, 'fa-caret-up')
//    }
//
//    Array.prototype.forEach.call(els, function(el) {
//        if (newcolor == 'red') {
//            el.className = el.className.replace(/\btext-green\b/g, 'text-red')
//            el.className = el.className.replace(/\bbg-green\b/g, 'bg-red')
//            el.className = el.className.replace(/\bborder-green\b/g, 'border-red')
//        } else {
//            el.className = el.className.replace(/\btext-red\b/g, 'text-green')
//            el.className = el.className.replace(/\bbg-red\b/g, 'bg-green')
//            el.className = el.className.replace(/\bborder-red\b/g, 'border-green')
//        }
//    })
//
//    if (growth_trend < 0) {
//        // even though its called doubling_rate it is actually half-life, bad naming, but we are just
//        // updating some visuals so should be fine for now
//        var doubling_rate = Math.round(Math.log(1/2) / Math.log(1 + growth_trend / 100))
//        document.getElementById('doubling-rate').innerText = 'half life'
//
//        if (growth_trend <= growth_trend_prev) {
//            var caret = 'fa-caret-down'
//        } else {
//            var caret = 'fa-caret-up'
//        }
//    } else {
//        var doubling_rate = Math.round(Math.log(2) / Math.log(1 + growth_trend / 100))
//        document.getElementById('doubling-rate').innerText = 'doubling rate'
//
//        if (growth_trend_prev < growth_trend) {
//            var caret = 'fa-caret-down'
//        } else {
//            var caret = 'fa-caret-up'
//        }
//    }
//
//    var el = document.getElementById('doubling-rate-arrow')
//    if (caret == 'fa-caret-down') {
//        el.className = el.className.replace(/\bfa-caret-up\b/g, caret)
//    } else {
//        el.className = el.className.replace(/\bfa-caret-down\b/g, caret)
//    }
//
//    document.getElementById('doubling-rate-val').innerHTML = Math.abs(doubling_rate)
//
//    console.log(beds_for_covid)
//
//    var icu_num_patients_chart = new Chart(document.getElementById("icu-num-patients"), {
//        type: 'line',
//        data: {
//            labels: xlabels,
//            datasets: [
//                {
//                    label: "ICU bed limit for COVID patients",
//                    data: beds_for_covid,
//                    fill: false,
//                    backgroundColor: "rgba(192, 192, 192, .5)",
//                    borderColor: "rgba(192, 192, 192, .5)",
//                    lineTension: 0,
//                    pointRadius: 3,
//                    pointHoverRadius: 10,
//                    borderDash: [10,5],
//                    spanGaps: true
//                },
//                {
//                    label: "ICU bed limit for COVID and non-COVID patients",
//                    data: beds,
//                    fill: false,
//                    backgroundColor: "rgba(0, 0, 0, .5)",
//                    borderColor: "rgba(0, 0, 0, .5)",
//                    lineTension: 0,
//                    pointRadius: 3,
//                    pointHoverRadius: 10,
//                    borderDash: [10,5],
//                    spanGaps: true
//                },
//                {
//                    label: "Confirmed COVID patients in ICU",
//                    data: patients_in_icu.slice(0, -3),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 192, 1)",
//                    borderColor: "rgba(75, 192, 192, 1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Points still being updated by ICUs",
//                    data: null_array(patients_in_icu.length - 4).concat(patients_in_icu.slice(-4)),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 192, .5)",
//                    borderColor: "rgba(75, 192, 192, .1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                }
//            ]
//        },
//        options: {
//            scales: {
//                yAxes: [{
//                    scaleLabel: {
//                        display: true,
//                        labelString: 'number of patients'
//                    }
//                }]
//            },
//            tooltips: tooltip_config,
//            animation: animations_config,
//            maintainAspectRatio: false
//        }
//    })
//
//    var icu_growth_chart = new Chart(document.getElementById("icu-growth"), {
//        type: 'line',
//        data: {
//            labels: xlabels,
//            datasets: [
//                {
//                    label: "Growth of confirmed patients in ICU",
//                    data: growth.slice(0, -3),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 192, .3)",
//                    borderColor: "rgba(75, 192, 192, .3)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Points still being updated by ICUs",
//                    data: null_array(growth.length - 4).concat(growth.slice(-4)),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 192, .1)",
//                    borderColor: "rgba(75, 192, 192, .1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Simple Moving Average (5 days)",
//                    data: growth_sma5,
//                    fill: false,
//                    backgroundColor: "rgba(192, 75, 192, 1)",
//                    borderColor: "rgba(192, 75, 192, 1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                }
//            ]
//        },
//        options: {
//            scales: {
//                yAxes: [{
//                    scaleLabel: {
//                        display: true,
//                        labelString: 'percentage change'
//                    }
//                }]
//            },
//            animation: animations_config,
//            tooltips: tooltip_config,
//            maintainAspectRatio: false
//        }
//    })
//
//    var icu_mortality_chart = new Chart(document.getElementById("icu-mortality-rate"), {
//        type: 'line',
//        data: {
//            labels: xlabels,
//            datasets: [
//                {
//                    label: "Evolution of mortality rate in ICU",
//                    data: mortality_rate.slice(0, -3),
//                    fill: false,
//                    backgroundColor: "rgba(192, 75, 75, 1)",
//                    borderColor: "rgba(192, 75, 75, 1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Points still being updated by ICUs",
//                    data: null_array(mortality_rate.length - 4).concat(mortality_rate.slice(-4)),
//                    fill: false,
//                    backgroundColor: "rgba(192, 75, 75, .5)",
//                    borderColor: "rgba(192, 75, 75, .5)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//            ]
//        },
//        options: {
//            scales: {
//                yAxes: [{
//                    scaleLabel: {
//                        display: true,
//                        labelString: 'percentage of patients'
//                    }
//                }]
//            },
//            animation: animations_config,
//            tooltips: tooltip_config,
//            maintainAspectRatio: false
//        }
//    })
//
//    var icu_recover_vs_death_chart = new Chart(document.getElementById("icu-recovery-vs-death"), {
//        type: 'line',
//        data: {
//            labels: xlabels,
//            datasets: [
//                {
//                    label: "Patients recovered from ICU",
//                    data: recovered.slice(0, -3),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 75, 1)",
//                    borderColor: "rgba(75, 192, 75, 1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Points still being updated by ICUs",
//                    data: null_array(recovered.length - 4).concat(recovered.slice(-4)),
//                    fill: false,
//                    backgroundColor: "rgba(75, 192, 75, .5)",
//                    borderColor: "rgba(75, 192, 75, .5)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Patients died in ICU",
//                    data: deaths.slice(0, -3),
//                    fill: false,
//                    backgroundColor: "rgba(192, 75, 75, 1)",
//                    borderColor: "rgba(192, 75, 75, 1)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//                {
//                    label: "Points still being updated by ICUs",
//                    data: null_array(deaths.length - 4).concat(deaths.slice(-4)),
//                    fill: false,
//                    backgroundColor: "rgba(192, 75, 75, .5)",
//                    borderColor: "rgba(192, 75, 75, .5)",
//                    lineTension: 0.1,
//                    pointRadius: 3,
//                    pointHoverRadius: 10
//                },
//            ]
//        },
//        options: {
//            scales: {
//                yAxes: [{
//                    scaleLabel: {
//                        display: true,
//                        labelString: 'number of patients'
//                    }
//                }]
//            },
//            animation: animations_config,
//            tooltips: tooltip_config,
//            maintainAspectRatio: false
//        }
//    })
//
//}

//document.addEventListener("DOMContentLoaded", function(e) {
document.update = update // bind to document scope so we can use it from the console
update()
setInterval(function () {
    update()
}, 600 * 1000) // update every 10 min
//})