"""Configuration dataclasses for the streaming framework."""

__author__ = "F.Feenstra"


from typing import Any, Dict, Tuple


class PlottingSetup:
    """
    Encapsulates matplotlib figure and axes configuration for streaming visualizations.
    
    This class serves as a centralized container for managing plot setup state,
    including figure/axes references, artist collections, and axis limits. It provides
    a clean interface for initializing and configuring matplotlib plots used in
    real-time streaming applications.
    
    Attributes:
        fig (Any): Matplotlib Figure instance. Typically created via plt.figure()
                   or plt.subplots() before passing to this class.
        ax (Any): Matplotlib Axes instance where data will be rendered. This is
                  the primary plotting surface for streaming visualizations.
        artists (Dict[str, Any]): Dictionary mapping names to matplotlib artists
                                  (lines, markers, patches, etc.) managed by this
                                  setup. Enables organized retrieval and updates
                                  during animation loops. Defaults to empty dict.
        xlim (Tuple[float, float] | None): Optional x-axis bounds as (min, max).
                                           If None, axes auto-scale. Defaults to None.
        ylim (Tuple[float, float] | None): Optional y-axis bounds as (min, max).
                                           If None, axes auto-scale. Defaults to None.
        title (str): Plot title displayed above the axes. 
                     Defaults to "Streaming Data Visualization".
    
    Methods:
        configure(): Applies the configured title and axis limits to the axes
                     instance. Should be called once during initialization.
    
    Example:
        >>> import matplotlib.pyplot as plt
        >>> fig, ax = plt.subplots()
        >>> setup = PlottingSetup(
        ...     fig=fig,
        ...     ax=ax,
        ...     xlim=(0, 100),
        ...     ylim=(-1, 1),
        ...     title="Real-time ECG Monitor"
        ... )
        >>> setup.configure()
        >>> # Later, store artists for tracking
        >>> setup.artists['signal'] = ax.plot([], [])[0]
    
    Note:
        The `Any` type hints for fig and ax are used for flexibility across
        matplotlib backends. In practice, these should be matplotlib.figure.Figure
        and matplotlib.axes.Axes instances respectively.
    
    See Also:
        StreamingRenderer: Base class that consumes PlottingSetup for rendering.
    """
    
    def __init__(
        self,
        fig: Any,
        ax: Any,
        artists: Dict[str, Any] = None,
        xlim: Tuple[float, float] = None,
        ylim: Tuple[float, float] = None,
        title: str = "Streaming Data Visualization"
    ):
        """
        Initialize a PlottingSetup instance.
        
        Args:
            fig: Matplotlib Figure instance.
            ax: Matplotlib Axes instance.
            artists: Dictionary of named artists. Defaults to empty dict.
            xlim: Optional x-axis bounds (min, max).
            ylim: Optional y-axis bounds (min, max).
            title: Plot title text.
        """
        self.fig = fig
        self.ax = ax
        # Handle mutable default safely
        self.artists = artists if artists is not None else {}
        self.xlim = xlim
        self.ylim = ylim
        self.title = title
    
    def configure(self) -> None:
        """
        Apply initial configuration to the axes instance.
        
        Sets the plot title and applies fixed axis limits if specified.
        This method should be called once after instantiation to ensure
        consistent initial plot appearance.
        
        Side Effects:
            Modifies the ax instance in-place by setting title and limits.
        
        Example:
            >>> setup = PlottingSetup(fig=fig, ax=ax, title="My Plot")
            >>> setup.configure()  # Title now visible on axes
        """
        self.ax.set_title(self.title)
        if self.xlim:
            self.ax.set_xlim(self.xlim)
        if self.ylim:
            self.ax.set_ylim(self.ylim)
    
    def __repr__(self) -> str:
        """
        Return a string representation for debugging.
        
        Returns:
            str: Human-readable representation of the instance state.
        """
        return (
            f"PlottingSetup("
            f"fig={self.fig!r}, "
            f"ax={self.ax!r}, "
            f"artists={self.artists!r}, "
            f"xlim={self.xlim!r}, "
            f"ylim={self.ylim!r}, "
            f"title={self.title!r}"
            f")"
        )