import os

from spanner import countdown


def row_iterator(filename, selected_cols=None, delimiter='\t', no_header=False,
                 return_header=False, num_header_lines_to_skip=0,
                 force_timer=False, timer_label=None):

    timer = init_timer(filename, force_timer, timer_label)

    with open(filename, 'r') as fh:
        while num_header_lines_to_skip > 0:
            fh.readline()
            num_header_lines_to_skip -= 1

        if no_header:
            if selected_cols is not None:
                col_indices = selected_cols
            else:
                col_indices = None
        else:
            header_line = fh.readline()
            col_names = header_line.rstrip().split(delimiter)
            col_indices = get_col_indices(selected_cols, col_names)

            if return_header:
                yield select_cols(col_indices, col_names)

        if timer is not None:
            timer.tick()

        line = fh.readline()

        while line:
            columns = line.rstrip('\r\n').split(delimiter)
            if col_indices is None:
                col_indices = range(len(columns))

            if len(columns) <= max(col_indices):
                print 'Warning - unexpected number of columns encountered.  Returning current result.'
                break

            yield select_cols(col_indices, columns)

            line = fh.readline()
            if timer is not None:
                timer.tick()


def load_dict(filename, key_cols, val_cols, delimiter='\t', force_unique_keys=False,
              no_header=False, num_header_lines_to_skip=0,
              force_timer=False, timer_label=None):
    
    timer = init_timer(filename, force_timer, timer_label)
    multiple_values_found_for_at_least_one_key = False

    with open(filename, 'r') as fh:
        while num_header_lines_to_skip > 0:
            fh.readline()
            num_header_lines_to_skip -= 1

        if no_header:
            key_indices = key_cols
            val_indices = val_cols
        else:
            header_line = fh.readline()
            col_names = header_line.rstrip().split(delimiter)
            key_indices = get_col_indices(key_cols, col_names)
            val_indices = get_col_indices(val_cols, col_names)

        if timer is not None:
            timer.tick()

        line = fh.readline()

        d = dict()
        while line:
            columns = line.rstrip('\r\n').split(delimiter)
            if len(columns) <= max(max(key_indices), max(val_indices)):
                print 'Warning - unexpected number of columns encountered.  Returning current result.'
                break

            key = select_cols(key_indices, columns)
            val = select_cols(val_indices, columns)

            if key in d:
                if force_unique_keys:
                    raise RuntimeError("Non-unique key encountered: " + str(key))

                if type(d[key]) is not set:
                    if val != d[key]:
                        multiple_values_found_for_at_least_one_key = True
                        d[key] = set([d[key]])
                        d[key].add(val)
                else:
                    d[key].add(val)
            else:
                d[key] = val

            if timer is not None:
                timer.tick()

            line = fh.readline()

    # force all values to lists if any key has multiple values
    if multiple_values_found_for_at_least_one_key:
        for key in d:
            if type(d[key]) is set:
                d[key] = list(d[key])
            else:
                d[key] = [d[key]]

    return d


def replace_values(filename, old_to_new, new_filename, delimiter='\t'):
    with open(new_filename, 'w') as ofh:
        for row in row_iterator(filename, return_header=True, delimiter=delimiter):
            cols = list(row)
            for old, new in old_to_new.items():
                try:
                    cols[cols.index(old)] = new
                except ValueError:
                    pass

            ofh.write('%s\n' % delimiter.join([str(x) for x in cols]))


def get_col_indices(selected_cols, col_names):
    # if no columns specified, get them all
    if selected_cols is None:
        return range(len(col_names))

    # if the columns are already specified as integer indices, there's nothing
    # further to do
    if type(selected_cols[0]) is int:
        return selected_cols

    selected_cols = [x.lower() for x in selected_cols]
    col_names = [x.lower() for x in col_names]

    indices = []
    for col in selected_cols:
        try:
            indices.append(col_names.index(col))
        except ValueError:
            raise Exception('Column not found: ' + col)

    return indices


def cast_to_original_data_type(value):
    try:
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            pass

    return value


def select_cols(indices, values):
    if len(indices) == 1:
        return cast_to_original_data_type(values[indices[0]])

    val = []
    for index in indices:
        value = cast_to_original_data_type(values[index])
        val.append(value)

    return tuple(val)


def init_timer(filename, force_timer=False, timer_label=None):
    if not os.path.isfile(filename):
        raise Exception('File does not exist: ' + filename)

    # always show timer if file is over 1GB
    if force_timer or (force_timer is None and os.path.getsize(filename) > 1024 * 1024 * 1024):
        print 'Determining line count of %s...' % filename
        assert os.path.exists(filename), 'File does not exist: ' + filename
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                pass

            linecount = i + 1

        if timer_label is None:
            timer_label = 'Reading file: %s' % filename

        return countdown.timer(total_iterations=linecount, label=timer_label)

    return None
