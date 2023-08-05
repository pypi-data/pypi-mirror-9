
_EXC_MSG = ('{exc_type_name}: {exc_msg} (line {exc_lineno} in file'
            ' {exc_filename}, logged from {callpoint_info})')


class Stats(object):
    def __init__(self, percentiles=DEFAULT_PERCENTILES):
        self.percentiles = percentiles

    def __getitem__(self, key):
        if key in self.measures:
            return self.measures[key].get_percentiles()
        return dict([(p, None) for p in self.percentiles])

    def __setitem__(self, key, val):
        if key in self.measures:
            self.measures[key].add_val(val)
        self.measures[key] = Measure(self.percentiles, val)

    def __repr__(self):
        avgs = dict([(k, v.sum / v.count) for
                     k, v in self.measures.items()])
        return "Stats(%r)" % avgs
