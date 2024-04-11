import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PlotType(Enum):
    TWO_D = "2d"
    ONE_D = "1d"


@dataclass
class Plot:
    type: PlotType
    x: List[float]
    errors: List[float]
    y: Optional[List[float]] = field(default_factory=list)
    x_ticks: Optional[List[float]] = field(default_factory=list)
    y_ticks: Optional[List[float]] = field(default_factory=list)


def generate_gaussian_data(mean, std_dev, count=1000):
    return [random.gauss(mean, std_dev) for _ in range(count)]


def simple_2d_gaussian():
    # Mean and standard deviation for x and y dimensions
    mean_x, std_dev_x = 0, 1
    mean_y, std_dev_y = 0, 1

    # Generate points
    x_points = generate_gaussian_data(mean_x, std_dev_x, count=1000)
    y_points = generate_gaussian_data(mean_y, std_dev_y, count=1000)
    errors = generate_gaussian_data(mean_y, std_dev_y, count=100)

    # Create Plot data class instance
    plot = Plot(type=random.choice([PlotType.ONE_D, PlotType.TWO_D]), x=x_points, y=y_points, errors=errors)

    # Return the plot data class
    return plot


def get_plots_for_reduction(reduction_id: int) -> List[Plot]:
    """
    Given a reduction id, return its pot
    :param reduction_id: The id of the reduction
    :return: The plot object
    """
    return [simple_2d_gaussian() for _ in range(3)]
