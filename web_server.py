from web.application import MJGApplication
from web.stats import StatsWebModule

MJGApplication(modules=[StatsWebModule]).start()
