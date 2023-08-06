import math
import faststat

import clastic

from support import context


def statgraphs(statname=''):
    body_parts = []
    for k, v in _filter_stats(statname).items():
        if not isinstance(v, (faststat.Stats, faststat.Duration, faststat.Interval)):
            continue
        k = k.replace('.', '_').replace('(', '_').replace(')', '')
        body_parts.append(
            ('<h2>{0}</h2>\n'
            '<div id="histogram-stat-{0}"></div>\n'
            '<div id="time-stat-{0}"></div>\n').format(k))
        body_parts.append(
            ('<script type="text/javascript">'
            '   stat_{0} = {1};\n'
            '   faststat_histogram_chart(stat_{0}, "#histogram-stat-{0}");\n'
            '   faststat_time_chart(stat_{0}, "#time-stat-{0}");\n'
            '</script>').format(k, faststat.stat2json(v)))
    return clastic.Response(
        TEMPLATE.replace('==BODY==', ''.join(body_parts)), mimetype="text/html")


def get_stats(the_stat=''):
    matches = _filter_stats(the_stat)
    brief = len(matches) > 1
    return dict([(k, _any2dict(v, brief)) for k,v in matches.items()])


def _any2dict(stat, brief=True):
    if type(stat) is context.StreamSketch:
        return _sketch2dict(stat, brief)
    elif type(stat) is faststat.Markov:
        return _markovstats2dict(stat, brief)
    return _stats2dict(stat, brief)


def _filter_stats(prefix):
    out = {}
    ctx = context.get_context()
    # pick up numerical stats
    stat_dict_names = (
        "stats", "durations", "intervals", "volatile_stats", "markov_stats", "sketches")
    for stat_dict_name in stat_dict_names:
        stats = getattr(ctx, stat_dict_name)
        out.update([(k, v) for k,v in stats.items() if prefix in k])
    return out


def _sigfigs(n, sigfigs=3):
    'helper function to round a number to significant figures'
    n = float(n)
    if n == 0 or math.isnan(n) or math.isinf(n):  # avoid math domain errors
        return n
    return round(n, -int(math.floor(math.log10(abs(n))) - sigfigs + 1))


def _stats2dict(stat, brief=True):
    if isinstance(stat, faststat.Markov):
        return _markovstats2dict(stat, brief)
    round_attrs = ("mean", "max", "min", "variance", "skewness", "kurtosis")
    exact_attrs = ("n", "lasttime", "maxtime", "mintime")
    if brief:
        round_attrs = round_attrs[:3]
        exact_attrs = exact_attrs[:2]
        # percentiles = (0.5, 0.95, 0.99)
    stat_dict = {}
    for a in round_attrs:
        stat_dict[a] = _sigfigs(getattr(stat, a))
    for a in exact_attrs:
        stat_dict[a] = getattr(stat, a)
    if brief:
        p = stat.percentiles
        stat_dict["percentiles"] = {
            0.5: _sigfigs(p[0.5]), 0.95: _sigfigs(p[0.95]), 0.99: _sigfigs(p[0.99])
        }
    else:
        ptiles = {}
        for p, v in stat.percentiles.items():
            ptiles[round(p, 2)] = _sigfigs(v)
        buckets = {}
        for p, v in stat.buckets.items():
            if p is None:
                buckets["overflow"] = v
            else:  # convert values from ns to ms
                buckets[_sigfigs(p / 10 ** 6)] = v
        stat_dict["percentiles"] = ptiles
        stat_dict["buckets(ms)"] = buckets
        if stat.interval:
            stat_dict["interval"] = _stats2dict(stat.interval, False)
    if stat.n < 64:  # TODO use stat.num_prev after updating to latest faststat
        for k in stat_dict["percentiles"].keys():
            stat_dict["percentiles"][k] = "(insufficient data)"
        if stat.n:  # if there is at least one data point, report the exact median
            sofar = sorted([stat.get_prev(i)[1] for i in range(stat.n)])
            stat_dict["percentiles"][0.5] = _sigfigs(sofar[len(sofar) / 2])
    if not brief:
        stat_dict['recent_points'] = [stat.get_prev(i) for i in range(stat.num_prev)]
        stat_dict['window_median'] = stat.window_median
        stat_dict['exponential_averages'] = stat.expo_avgs
        stat_dict['lag_averages'] = stat.lag_avgs
    return stat_dict


def _markovstats2dict(markov, brief=True):
    states = {}
    total_time = sum([d.n * d.mean for d in markov.state_durations.values()])
    for name, duration in markov.state_durations.items():
        if brief:
            if total_time:
                percent = _sigfigs(duration.n * duration.mean / total_time, 2)
                mean_ms = _sigfigs(duration.mean / 1e6)
                states[name] = {'percent': percent, 'mean(ms)': mean_ms}
            else:
                states[name] = {'percent': 0, 'mean(ms)': mean_ms}
        else:
            states[name] = _stats2dict(duration, True)
    state_counts = {}
    for name, stats in markov.state_counts.items():
        if brief:
            state_counts[name] = _sigfigs(stats.mean)
        else:
            state_counts[name] = _stats2dict(stats, True)
    transitions = {}
    for name, interval in markov.transition_intervals.items():
        name = repr(name)
        if brief:
            transitions[name] = interval.n + 1
        else:
            transitions[name] = _stats2dict(interval, True)
    return {"states": states, "transitions": transitions, "state_counts": state_counts}


def _sketch2dict(sketch, brief=True):
    heavy_hitters = sketch.heavy_hitters()
    if brief:
        heavy_hitters = dict(
            sorted(heavy_hitters.items(), key=lambda e: e[1][0])[-8:])
    heavy_hitters = dict(
        [(repr(k), [v[0], v[0] + v[1]]) for k, v in heavy_hitters.items()])
    return {
        "n": sketch.n,
        "cardinality": sketch.card(),
        "common_elements": heavy_hitters,
    }


TEMPLATE = ('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
''' + faststat.JAVASCRIPT_HTML_HEAD +
'''</head>
<body>
==BODY==
</body>
</html>''')

