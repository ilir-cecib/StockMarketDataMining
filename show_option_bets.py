import numpy as np
import argparse
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
matplotlib.rcParams.update({'font.size': 18})
plt.rcParams['figure.figsize'] = [20, 10]
import pandas as pd
#The following line will fix a pandas issue in Utuntu.
pd.core.common.is_list_like = pd.api.types.is_list_like
from options import Options


def get_option_data(ticker, month, year, expiration_date):
    ''' 
        Get option data from Yahoo. 
    '''
    option = Options(ticker)
    raw_data = option.get_options_data(month=month, year=year)
    current_price = raw_data.Underlying_Price.iloc[0]

    # Reset multi-index to simple index, to make working with dataframe columns easier. 
    raw_data.reset_index(inplace=True)         

    # Select target date for visualization, and remove outliers (based on FILTER_STOCK_CHANGE param)
    raw_data_for_date = raw_data[raw_data.Expiry==expiration_date]
    filtered_data = raw_data_for_date[abs((raw_data_for_date.Strike - current_price)/current_price) 
            <= FILTER_STOCK_CHANGE]

    # Add new column in dataframe with percentage change values.
    extracted_vals = np.vstack(filtered_data.Strike.apply((
        lambda x: (x - current_price)/current_price)))
    filtered_data['percentage_change' % current_price] = extracted_vals[:,0]

    # Split calls and puts
    filtered_calls = filtered_data[filtered_data.Type=='call']
    filtered_puts = filtered_data[filtered_data.Type=='put']

    return filtered_calls, filtered_puts, current_price



def visualize_call_put_volume_in_bubble_plot(calls, puts, stock_price):
    '''
        Bubble Plot: Plot Premium/Strike relation.
    '''
    # Create primary and secondary subplot in the figure. 
    fig = plt.figure(constrained_layout=True)    
    gs = GridSpec(1, 4, figure=fig)
    ax = fig.add_subplot(gs[0,:3])
    ax1 = fig.add_subplot(gs[0,3]) 
    
    # Plot Volume for call and put options.
    ax.scatter(calls.Strike, calls.Last, marker='^', color='g',label='calls');
    ax.scatter(puts.Strike, puts.Last, marker='v', color='r', label='puts');

    a = min(calls.Vol.min(), puts.Vol.min())
    b = max(calls.Vol.max(), puts.Vol.max())
    r = b-a    
    normalize_marker_size = lambda x:VOLUME_MARKER_SCALE * ((x-a)/r)
    ax.scatter(calls.Strike, calls.Last, s=normalize_marker_size(calls.Vol), facecolors='none', 
            color='g', label='Call Volume');
    ax.scatter(puts.Strike, puts.Last, s=normalize_marker_size(puts.Vol), facecolors='none', 
            color='r', label='Put Volume');
    (y_min, y_max) = ax.get_ylim();
    ax.plot([stock_price, stock_price], [y_min, y_max], 'k--', label='Stock Price');
    ax.set_ylim(y_min, y_max);
    ax.legend()      
    ax.set_title('%s at %.2f, Expiry %s '% (TICKER, stock_price, EXPIRATION_DATE))
    ax.set_ylabel('Premium');
    ax.set_xlabel('Strike');
    ax.grid()

    # Create secondary axis to show percentage change. 
    ax2 = ax.twiny()
    x_tick_list = list(ax.get_xticks())
    ax2.set_xticks(x_tick_list)
    format_xticks = lambda x: '0' if x==0 else '%.1f' % (x*100)
    ax2.set_xticklabels([format_xticks(i) for i in (x_tick_list-stock_price)/stock_price])
    ax2.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
    ax2.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
    ax2.spines['bottom'].set_position(('outward', 80))
    ax2.set_xlabel('Percentage Change (%)')
    ax2.set_xlim(ax.get_xlim())

    # Show relative volume size in secondary subplot.
    vol_plot_y = np.linspace(a+1, b, VOLUME_GRANULARITY)
    vol_plot_x = VOLUME_GRANULARITY*[1] 
    ax1.scatter(vol_plot_x, vol_plot_y, s=normalize_marker_size(vol_plot_y),
            facecolors='none', color='k')
    ax1.set_xticklabels([])
    ax1.set_title('Volume Size')
    (y_min, y_max) = ax1.get_ylim();
    yaxis_extra_margin = r/VOLUME_GRANULARITY
    ax1.set_ylim(y_min, y_max+r/yaxis_extra_margin);
    ax1.yaxis.tick_right()
    fig.savefig('%s_%s_strike_and_premium.pdf' % (TICKER, EXPIRATION_DATE), bbox_inches='tight')



if __name__ == '__main__':

    # Global parameters to configure visualization. 
    FILTER_STOCK_CHANGE = 0.8
    VOLUME_GRANULARITY = 6    
    VOLUME_MARKER_SCALE = 6*10**3
    ITM_OPTION_VISUAZLIZATION_FILTER = 0.1

    # Global parameters to choose stock and target date.
    parser = argparse.ArgumentParser(
            description='Visualize stock option volume. E.g. python show_option_bets.py MSFT 2020-06-19')
    parser.add_argument('stock', type=str,
            help='Stock Ticker. E.g. MSFT, AAPL, etc.')
    parser.add_argument('expiration', type=str,
            help='Expiration date; required format yyyy-mm-dd. E.g. 2020-06-19.')
    args = parser.parse_args()
    TICKER = args.stock
    EXPIRATION_DATE = args.expiration
    month = int(EXPIRATION_DATE.split('-')[1])
    year = int(EXPIRATION_DATE.split('-')[0])

    # Get call and put dataframes, and latest stock price.
    call_df, put_df, current_stock_price = get_option_data(TICKER, month, year, EXPIRATION_DATE)

    # Filter out deep-in-the-money calls and puts.
    itm_call_filter = current_stock_price * (1 - ITM_OPTION_VISUAZLIZATION_FILTER)
    itm_put_filter = current_stock_price * (1 + ITM_OPTION_VISUAZLIZATION_FILTER)
    filtered_call_df = call_df[call_df.Strike >= itm_call_filter]
    filtered_put_df = put_df[put_df.Strike <= itm_put_filter]

    # Visualize and save plot locally.  
    visualize_call_put_volume_in_bubble_plot(filtered_call_df, filtered_put_df, current_stock_price)
