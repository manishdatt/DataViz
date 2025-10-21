# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.7",
#     "numpy==2.2.6",
#     "pandas==2.3.3",
#     "plotly==6.3.1",
#     "seaborn==0.13.2",
# ]
# ///

import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import textwrap
    return cm, mcolors, pd, plt, sns, textwrap


@app.cell
def _(pd):
    historic_station_met = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-10-21/historic_station_met.csv')
    station_meta = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-10-21/station_meta.csv')
    return (historic_station_met,)


@app.cell
def _(historic_station_met):
    historic_station_met
    return


@app.cell
def _(historic_station_met, pd):
    historic_station_met['year'] = pd.to_datetime(historic_station_met['year']).astype(int)
    return


@app.cell
def _(historic_station_met, pd):
    bins = [1850, 1925, 1950, 1975, 2000, 2025]
    labels = ['till 1925', '1926–1950', '1951–1975', '1976–2000', '2001 onwards']
    historic_station_met['quarter'] = pd.cut(historic_station_met['year'], bins=bins, labels=labels)
    return


@app.cell
def _(historic_station_met):
    historic_station_met['tdiff'] = historic_station_met['tmax']-historic_station_met['tmin']
    historic_station_met['station'] = historic_station_met['station'].str.capitalize()
    return


@app.cell
def _(historic_station_met):
    historic_station_met.columns
    return


@app.cell
def _(historic_station_met):
    df_grp = historic_station_met.groupby(['station','year', 'month', 'quarter']).agg({
        'tmax': 'max',
        'tmin': 'min',
        'tdiff': 'mean',
        'af': 'sum',
        'rain': 'sum',
         'sun': 'sum'
    }).reset_index()
    df_grp
    return (df_grp,)


@app.cell
def _(historic_station_met, pd):
    # Group by both station and year
    grouped = historic_station_met.groupby(['station', 'year'])

    # Dictionary to store correlation results
    correlations = {}

    # Loop through each (station, year) group
    for (station, year), df_grp1 in grouped:
        # Compute correlation between 'rain' and 'sun'
        corr_matrix = df_grp1[['rain', 'sun']].corr()
        corr_value = corr_matrix.loc['rain', 'sun']

        # Store result with a tuple key
        correlations[(station, year)] = corr_value

    correlation_df = pd.DataFrame.from_dict(
        correlations, orient='index', columns=['rain_sun_corr']
    )

    # Split the tuple index into two columns
    correlation_df.index = pd.MultiIndex.from_tuples(correlation_df.index, names=['station', 'year'])
    correlation_df = correlation_df.reset_index()

    print(correlation_df)
    return (correlation_df,)


@app.cell
def _(correlation_df, plt, sns):
    sns.scatterplot(data=correlation_df, x='year', y='rain_sun_corr', hue='station', alpha=0.5, legend=False)
    plt.show()
    return


@app.cell
def _(df_grp):
    df_grp[df_grp['quarter'] == '1926–1950']
    return


@app.cell
def _():
    #col_palatte = 'Wistia'
    #fig,ax = plt.subplots(1,2, figsize=(12,5), sharey=True)
    #sns.stripplot(data=df_grp[df_grp['quarter'] == 'till 1925'],x='month',y='rain', hue='sun', ax=ax[0], palette=col_palatte, dodge=True)
    #sns.stripplot(data=df_grp[df_grp['quarter'] == '2001 onwards'],x='month',y='rain', hue='sun', ax=ax[1], palette=col_palatte, dodge=True)
    return


@app.cell
def _(cm, df_grp, mcolors, plt, sns, textwrap):
    col_palette = 'autumn_r' #'Wistia'
    month_labels = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    sns.set_context("talk", font_scale=2.2)  
    bg_color = '#390099'
    fg_color = '#eef4ed'

    # Create a faceted stripplot

    g = sns.catplot(
        data=df_grp,
        x='month',
        y='tmax',
        hue='tdiff',
        col='station',
        kind='strip',
        palette=col_palette,
        dodge=False,
        sharey=True,
        height=5,
        aspect=1.2,
        col_wrap=8,
        legend=False,
    )
    g.fig.patch.set_facecolor(bg_color)  

    # Set axes background color
    for ax in g.axes.flat:
        ax.set_facecolor(bg_color)  
        ax.tick_params(axis='y', colors=fg_color)
        for spine in ax.spines.values():
            spine.set_color(fg_color)

    col_wrap = 8

    for i, ax in enumerate(g.axes.flat):
        if i % col_wrap != 0:  # Not the first column in each row
            ax.set_ylabel('')
            ax.tick_params(axis='y', left=False, labelleft=False, colors=fg_color)
            ax.tick_params(axis='x', colors=fg_color)
            sns.despine(ax=ax,left=True)

    # Adjust layout
    g.set_titles("{col_name}", color=fg_color)
    g.set_axis_labels("", "")
    g.set_xticklabels(month_labels, fontdict={'family': 'monospace', 'color': fg_color})
    g.fig.text(-0.005, 0.5, 'Maximum temperature (°C)', va='center', rotation='vertical', color=fg_color)

    norm = mcolors.Normalize(vmin=df_grp['tdiff'].min(), vmax=df_grp['tdiff'].max())
    sm = cm.ScalarMappable(cmap='autumn_r', norm=norm)
    sm.set_array([])  # Required for colorbar

    #g.fig.subplots_adjust(right=0.85)
    # Add the colorbar to the figure
    cbar_ax = g.fig.add_axes([0.7, 0.08, 0.2, 0.01])  # [left, bottom, width, height]
    cbar = g.fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Temperature Difference', color=fg_color)

    # Change tick label color
    cbar.ax.xaxis.set_tick_params(color=fg_color)  # Tick marks
    for label in cbar.ax.get_xticklabels():
        label.set_color(fg_color)  # Tick label text
    title = 'Monthly variations in maximum temperature at 37 weather stations in the UK. Points are colored based on the difference in maximum and minimum temperatures.'    

    g.fig.text(0.63, 0.13,textwrap.fill(title, width=55), color=fg_color, family='Serif', fontweight='bold', fontsize=40)           
    plt.tight_layout()
    plt.savefig("UK_weather.png", dpi=300, bbox_inches='tight')
    plt.show()
    return


if __name__ == "__main__":
    app.run()
