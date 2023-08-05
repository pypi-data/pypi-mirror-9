import os
import sys

sys.path.append(os.path.dirname(__name__))

from example import create_app

# create an app instance
app = create_app()
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.run(debug=True)
