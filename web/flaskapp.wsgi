#flaskapp.wsgi
import sys
sys.path.insert(0, '/var/www/html/AdvDistSystems/web')

from app import app as application
