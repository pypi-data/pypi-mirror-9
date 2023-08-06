from collections import OrderedDict
import time

try:
    from IPython.html import widgets
    from IPython import display
except:
    pass  # not currently in an ipython env

###################################

last_keystroke = time.time()
def search_select(df, search_cols, callback, mode='flat', search_on_type=True,
                  initial_filter='', label=None):
    """
    Creates and displays searchable selector(s).  In "flat" mode, the provided
    columns are combined into one searchable field.  In "nested" mode, a
    separate dropdown is provided for each column; selecting from one column
    will restrict the options present in subsequent columns.  In "nested" mode,
    only the last column is searchable
    """

    assert mode in ('flat', 'nested', 'all'), \
        'Please select "flat", "nested" or "all" for mode'

    if len(search_cols) < 2:
        mode = 'flat'

    disp_cols = []
    id_cols = []
    for col in search_cols:
        if isinstance(col, tuple):
            disp_col, id_col = col
        else:
            disp_col = id_col = col
        disp_cols.append(disp_col)
        id_cols.append(id_col)

    def populate_options(ww):
        if wfilter.value != '':
            s = [False] * len(df)
            for st in wfilter.value.split('|'):
                s |= df[disp_cols].apply(lambda r:
                                            any([st.lower()
                                                 in c.lower()
                                                 for c in r]),
                                         axis=1)
        else:
            s = [True] * len(df)

        if ww not in sorted_selectors:  # flat_selector
            disp_vals = ['--'.join(x) for x in df[s].sort(disp_cols)[disp_cols].values]
            id_vals = [tuple(x) for x in df[s].sort(disp_cols)[id_cols].values]

            if len(disp_vals) > 0:
                ww.values = OrderedDict((disp, idx)
                                        for disp, idx in zip(disp_vals, id_vals))
            else:
                ww.values = {'': -1}

        else:
            i = sorted_selectors.index(ww)
            for j in xrange(i):
                wprev = sorted_selectors[j]
                s &= df[id_cols[j]] == wprev.value

            vals = sorted(set(tuple(x)
                              for x in df[s][[disp_cols[i], id_cols[i]]].values))
            if len(vals) > 0:
                ww.values = OrderedDict((str(disp), idx)
                                        for disp, idx in vals)
            else:
                ww.values = {'': -1}

        if len(ww.values) > 0:
            ww.value = ww.values.values()[0]
        else:
            ww.value = None

    sorted_selectors = []
    widgets_to_update_on_search = []
    if mode in ('nested', 'all'):
        def make_callback(w):
            def on_selection():
                i = sorted_selectors.index(w)
                if i == len(search_cols) - 1:
                    callback(tuple(ww.value for ww in sorted_selectors))
                else:
                    populate_options(sorted_selectors[i+1])
            return on_selection

        for col in disp_cols:
            w = widgets.DropdownWidget(description=col)
            w.on_trait_change(make_callback(w), 'value')
            sorted_selectors.append(w)

        # only need to update the first - the others will be triggered
        widgets_to_update_on_search.append(sorted_selectors[0])

    all_widgets = sorted_selectors[:]
    if mode in ('flat', 'all'):
        wflat = widgets.DropdownWidget(
            description=label if mode == 'flat' else 'All')
        wflat.on_trait_change(lambda: callback(wflat.value), 'value')
        all_widgets.append(wflat)
        widgets_to_update_on_search.append(wflat)

    wfilter = widgets.TextWidget(description='Filter', value=initial_filter)
    all_widgets.append(wfilter)

    def update_options(w=None):
        for w in widgets_to_update_on_search:
            populate_options(w)

    if search_on_type:
        def update_on_keystroke():
            global last_keystroke
            now = time.time()
            if now > last_keystroke + 1:
                update_options()

        wfilter.on_trait_change(update_on_keystroke, 'value')
    else:
        b = widgets.ButtonWidget(description='Search')
        b.on_click(update_options)
        all_widgets.append(b)

    container = widgets.ContainerWidget()
    display.display(container)
    if mode == 'flat':
        container.remove_class('vbox')
        container.add_class('hbox')

    container.children = all_widgets
    update_options()

    return container


################################


def inline_folium_map(map, width=1000, height=600, reset_display=True):
    """
    Convenience method for in-lining folium maps directly in ipython notebooks
    """
    map.create_map()
    srcdoc = map.HTML.replace('"', '&quot;')
    embed = display.HTML('<iframe srcdoc="{}" '
                         'style="width: {}px; height: {}px; '
                         'border: none"></iframe>'
                         .format(srcdoc, width, height))

    if reset_display:
        display.clear_output(wait=True)

    display.display(embed)
    return embed
