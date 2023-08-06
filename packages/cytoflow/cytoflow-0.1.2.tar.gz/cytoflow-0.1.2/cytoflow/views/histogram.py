from traits.api import HasTraits, Str, provides
import matplotlib.pyplot as plt
import seaborn as sns
from cytoflow.views.i_view import IView

@provides(IView)
class HistogramView(HasTraits):
    """Plots a one-channel histogram
    
    Attributes
    ----------
    name : Str
        The HistogramView name (for serialization, UI etc.)
    
    channel : Str
        the name of the channel we're plotting
    
    xfacet : Str 
        the conditioning variable for multiple plots (horizontal)
    
    yfacet : Str
        the conditioning variable for multiple plots (vertical)
    
    huefacet : Str
        the conditioning variable for multiple plots (color)
        
    subset : Str
        a string passed to pandas.DataFrame.query() to subset the data before 
        we plot it.
        
        .. note: Should this be a param instead?
    """
    
    # traits    
    name = Str
    channel = Str
    xfacet = Str
    yfacet = Str
    huefacet = Str
    subset = Str
    
    def plot(self, experiment, **kwargs):
        """Plot a faceted histogram view of a channel"""
        
        kwargs.setdefault('histtype', 'stepfilled')
        kwargs.setdefault('alpha', 0.5)
        kwargs.setdefault('bins', 200) # Do not move above
        
        if not self.subset:
            x = experiment.data
        else:
            x = experiment.query(self.subset)

        g = sns.FacetGrid(x, 
                          col = (self.xfacet if self.xfacet else None),
                          row = (self.yfacet if self.yfacet else None),
                          hue = (self.huefacet if self.huefacet else None))
        
        g.map(plt.hist, self.channel, **kwargs)
        
        
    def validate(self, experiment):
        """Validate this view against an experiment."""
    