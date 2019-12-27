from app import create_app, db
from app.models import User, Role, Language, Car, \
	CarLanguage
from app.cli import register as cli_register


app = create_app()
cli_register(app)

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 
			'User': User, 
			'Language': Language,
			'Car': Car,
			'CarLanguage': CarLanguage,
			'Role': Role}
