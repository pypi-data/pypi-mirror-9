# Create your views here.
import datetime
from django.views.generic import TemplateView
import sim
from pug.dj.miner.views import d3_plot_context
from models import Day, get_panel
from pug.nlp import util
import pandas as pd


class HomeView(TemplateView):
    """Query the miner.AggregateResults table to retrieve values for plotting in a bar chart"""
    template_name = 'invest/home.html'


class PlotSymbolView(TemplateView):
    """Query the miner.AggregateResults table to retrieve values for plotting in a bar chart"""
    template_name = 'miner/line_plot.d3.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PlotSymbolView, self).get_context_data(**kwargs)
        symbols = [sym.upper() for sym in util.normalize_names(self.kwargs['symbols'])]
        panel = get_panel(symbols=symbols).transpose(2,1,0)
        # TODO: test!
        # qs = []
        # for i, symbol in enumerate(panel.items):
        #     series = panel[symbol]['Adj Close']
        #     for date, value in zip(series.index, series.values):
        #         qs += [Day(date=datetime.date(row[0].year, row[0].month, row[0].day), close=row[i+1], symbol=symbol)]
        # Day.objects.bulk_create(qs)


        context['df'] = pd.DataFrame(panel['Adj Close']).sort_index()
        return d3_plot_context(context,
            table=context['df'], title='Price History', xlabel='Date', ylabel='Adjusted Close')


class PlotPredictionView(TemplateView):
    """Query the miner.AggregateResults table to retrieve values for plotting in a bar chart"""
    template_name = 'miner/line_plot.d3.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PlotSymbolView, self).get_context_data(**kwargs)
        symbols = sim.normalize_symbols(self.kwargs['symbols'])
        df = sim.price_dataframe(symbols=symbols,
            start=datetime.datetime(2010, 1, 1),
            end=datetime.datetime(2010, 12, 31),  
            price_type='close')
        # TODO: test!
        qs = []
        for i, symbol in enumerate(df.columns):
            for row in df.records():
                qs += [Day(date=datetime.date(row[0].year, row[0].month, row[0].day), close=row[i+1], symbol=symbol)]
        Day.objects.bulk_create(qs)

        context['df'] = df
        return d3_plot_context(context,
            table=df, title='Price History', xlabel='Date', ylabel='Adjusted Close')