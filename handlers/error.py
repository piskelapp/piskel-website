import os.path, traceback, logging
from base import BaseHandler

DEFAULT_ERROR = 500

class ErrorHandler(BaseHandler):
    def handle_error(self, exception):
        # Determine status code and set it
        status_int = hasattr(exception, 'status_int') and exception.status_int or DEFAULT_ERROR
        self.response.set_status(status_int)

        # Determine template file
        template_name = 'error/http-'+ str(DEFAULT_ERROR) +'.html'

        # Default to error 500 if we don't have template file for the specific error
        try:
            template_name = self.jinja2.environment.get_template('error/http-'+ str(status_int) +'.html').name
        except:
            pass

        values = {
            'exception': exception,
            'traceback': traceback.format_exc()
        }

        logging.error('Handled error: '+ str(status_int) +', exception message: '+ str(exception) +', traceback: '+ values['traceback'])

        self.render(template_name, values)