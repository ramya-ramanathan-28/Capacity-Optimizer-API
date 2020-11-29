from app import app
import logging
import os
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
port = int(os.getenv("PORT", 9099))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)