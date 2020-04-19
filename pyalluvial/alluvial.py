import numpy as np
import matplotlib.pyplot as plt

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def calc_sigmoid_line(width, y_start, y_end):
    xs = np.linspace(-5, 5, num=50)
    ys = np.array([sigmoid(x) for x in xs])
    xs = xs / 10 + 0.5 # これで0~1の範囲になる
    xs *= width
    ys = y_start + (y_end - y_start) * ys
    return xs, ys

def plot(df, xaxis_names, y_name, alluvium, order_dict=None, ignore_continuity=False, cmap_name='tab10', figsize=(6.4, 4.8)):
    '''
    Plot alluvial plot
    
    Parameters
    --------
    df: pandas DataFrame
        df must be in wide format, as shown in the example below.
        Example)
        |    |   survived | class   | sex    |   freq |
        |---:|-----------:|:--------|:-------|-------:|
        |  0 |          0 | First   | female |      3 |
        |  1 |          0 | First   | male   |     77 |
        |  2 |          0 | Second  | female |      6 |
        |  3 |          0 | Second  | male   |     91 |
        |  4 |          0 | Third   | female |     72 |
    xaxis_names: list of str
        Specify the column names to line up on the x-axis. It is drawn in the order of this list.
        Example) ['class', 'sex']
    y_name: str
        Specify a column name that represents the height of the y-axis.
        Example) 'freq'
    alluvium: str or None
        Specify the column name of the alluvial color. 
        If ignore_continuity is true and you want to reset the colors in each Stratum, set it to None.
        Example) 'survived'
    order_dict: dict
        If you want to adjust the order in each Stratum, specify the order like the following example.
        Example) {'class': ['Third', 'Second', 'First'], 'sex': ['male', 'female']}
    ignore_continuity: bool
        Specify True if you want to ignore the continuity of each axis, otherwise False.
        Example) True
    cmap_name: str
        Specify any matplotlib's colormap name you want to use in the following link.
        It is recommended to choose from the Qualitative colormaps.
        ref) https://matplotlib.org/examples/color/colormaps_reference.html
        Example) 'tab10'
    figsize: tuple of float
        Specify the figsize.
        Example) (10, 10)
        
    Return
    --------
    fig: matplotlib figure object
    '''
    df = df.copy()
        
    # 各stratumの高さを計算する
    stratum_dict = {}
    for xaxis in xaxis_names:
        stratum_dict[xaxis] = df.groupby(xaxis)[y_name].sum()
    
    # stratumの順番を設定する
    if order_dict is None:
        pass
    else:
        for key, orders in order_dict.items():
            stratum = stratum_dict[key]
            stratum_dict[key] = stratum[orders]

    fig, ax = plt.subplots(figsize=figsize)
    
    # plot stratum (stacked bar)
    for i, stratum in enumerate(stratum_dict.values()):
        xtick_label = stratum.index.name
        names = stratum.index.values
        values = stratum.values

        for j, (name, value) in enumerate(zip(names, values)):
            bottom = values[:j - len(stratum)].sum()
            rectangle = ax.bar(
                x=[i],
                height=value,
                bottom=bottom,
                color='white',
                edgecolor='black',
                fill=True,
                linewidth=1,
                width=0.4
            )
            text_y = rectangle[0].get_height() / 2 + bottom
            ax.text(x=i, y=text_y, s=name, horizontalalignment='center', verticalalignment='center')
    
    cmap = plt.get_cmap(cmap_name)

    # alluviumのcolor dictを作成する
    if alluvium is not None:
        color_val = df[alluvium].unique()
        color_dict = dict(zip(color_val, list(range(len(color_val)))))
    
    if ignore_continuity:
        for i in range(len(xaxis_names)):
            if i + 1 >= len(xaxis_names):
                break
            else:
                if alluvium is None:
                    alluvium = xaxis_names[i]
                    color_val = df[alluvium].unique()
                    color_dict = dict(zip(color_val, list(range(len(color_val)))))
                
                agg_cols = list(set([f'{alluvium}'] + xaxis_names[i: i+2]))
                df_agg = df.groupby(agg_cols, as_index=False)[y_name].sum()
                _plot_alluvium(df_agg, xaxis_names[i: i+2], y_name, alluvium, order_dict, color_dict, ax, cmap, i)
                alluvium = None
    else:
        _plot_alluvium(df, xaxis_names, y_name, alluvium, order_dict, color_dict, ax, cmap, 0)
                
    # set xticklabels
    ax.set_xticks(list(range(len(stratum_dict))))
    ax.set_xticklabels([stratum.index.name for stratum in stratum_dict.values()])
    
    return fig

def _plot_alluvium(df, xaxis_names, y_name, alluvium, order_dict, color_dict, ax, cmap, x_init=0):
    # 任意のalluviumの順番を設定する
    if order_dict is None:
        pass
    else:
        for key, orders in order_dict.items():
            if key in df.columns:
                df[f'{key}_order'] = df[key].map(dict(zip(orders, list(range(len(orders)))))).astype(int)
    # alluviumの高さを計算する
    for xaxis in xaxis_names:
        if xaxis + '_order' in df.columns:
            df = df.sort_values(xaxis + '_order')
        else:
            df = df.sort_values(xaxis)
        df[f'y_{xaxis}'] = df[y_name].cumsum().shift(1).fillna(0)

    # plot alluvium
    for i in range(len(xaxis_names)):
        if i + 1 >= len(xaxis_names):
            break
        else:
            for y_left, y_right, height, color_key in zip(
                df[f'y_{xaxis_names[i]}'].values,
                df[f'y_{xaxis_names[i + 1]}'].values,
                df[y_name].values,
                df[alluvium].values):

                xs, ys_under = calc_sigmoid_line(0.6, y_left, y_right)
                xs += i + 0.2
                ys_upper = ys_under + height

                ax.fill_between(xs + x_init, ys_under, ys_upper, alpha=0.7, color=cmap(color_dict.get(color_key)))