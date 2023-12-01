import plotly.graph_objects as go
from functools import wraps
import time
from collections import defaultdict


class testflow:
    """Class for capturing function execution times, creating visualizations, and updating the visualizations with live data."""

    def __init__(self):
        """Initializes the class attributes and sets the default time delay for live updates."""
        self.clean()
        self.timedelay = 0.3

    def clean(self):
        """Resets the class attributes to default values."""
        self.all_lists = defaultdict(lambda: {'time': [], 'answer': []})
        self.cache = []
        self.trace_count = 0
        self.figure_cache = []
        self.sync = {}
        self.argument = defaultdict(list)

    def timeit(self, func):
        """Decorator that calculates and returns the execution time of a function."""
        @wraps(func)
        def timeit_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            return result, total_time
        return timeit_wrapper

    def visual(self):
        """Creates a new figure for visualization using the plotly library."""
        self.fig = go.FigureWidget()
        self.fig.update_layout(template="plotly_white")
        self.fig['layout']['yaxis'].update(title_text='time spent, s')
        self.fig['layout']['xaxis'].update(title_text='# points')
        self.fig.update_layout(legend=dict(x=0.1, y=.5, font=dict(size=15, color="grey")),
                               margin=dict(l=10, r=10, t=10, b=10))
        return self.fig

    def live(self, **kwargs):
        """Updates the live visualization with new data."""
        for name, value in kwargs.items():
            self.argument[name].append(value)
        time.sleep(self.timedelay)
        for items in self.all_lists.keys():
            if items not in self.figure_cache:
                self.fig.add_trace(go.Scatter(
                    name=items, fill='tonexty', fillcolor='rgba(0,250,0,0.4)'))
                self.sync[items] = self.trace_count
                self.figure_cache.append(items)
                self.trace_count += 1
            self.fig.data[self.sync[items]].y = self.all_lists[items]['time']
            if self.argument != {}:
                self.fig.data[self.sync[items]].x = self.argument[name]
                self.fig['layout']['xaxis'].update(title_text=name)

    def resolve(self, func):
        """Decorator that calculates the execution time of a function and stores the result."""
        @wraps(func)
        def timeit_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            self.all_lists[func.__name__]['time'].append(total_time)
            self.all_lists[func.__name__]['answer'].append(result)
            return result, total_time
        return timeit_wrapper
