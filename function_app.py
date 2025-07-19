""" Azure Function for dailyemailnewsdigests """
import azure.functions as func
from src.dailyemailnewsdigests.blueprints.bp_digests import bp as bp_digests

# Set a default authentication level for any future HTTP triggers
app = func.FunctionApp()

app.register_blueprint(bp_digests)
