"""Azure Function app entry point for dailyemailnewsdigests."""

import azure.functions as func

from src.dailyemailnewsdigests.blueprints.bp_digests import bp as bp_digests
from src.dailyemailnewsdigests.blueprints.bp_rss_fetcher import bp as bp_rss_fetcher

app = func.FunctionApp()

app.register_blueprint(bp_digests)
app.register_blueprint(bp_rss_fetcher)
