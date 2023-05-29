# Import the logging module, a standard Python module for event logging.
import logging

# Create a logger object with the name of the current module. This object provides the interface to add logging
# statements in your code.
logger = logging.getLogger(__name__)

# Set the threshold for this logger to ERROR. This means that only events of this level and above will be tracked,
# unless the logging package is configured differently.
logger.setLevel(logging.ERROR)

# Set the threshold for this logger to INFO. This will overwrite the previous level set to ERROR. It means that
# events of this level and above will be tracked, unless the logging package is configured differently.
logger.setLevel(logging.INFO)

# Create a file handler for your logger that writes log messages to a file named 'logfile.log'.
file_handler = logging.FileHandler('logfile.log')

# Define a formatter that specifies the layout of log messages. This one includes the time of logging, the logging
# level, the logger's name, and the message.
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

# Add the formatter to the file handler, so that it knows how to format the log messages.
file_handler.setFormatter(formatter)

# Add the file handler to the logger, so that it can direct its log messages to the file specified by the handler.
logger.addHandler(file_handler)
