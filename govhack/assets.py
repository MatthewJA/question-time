from flask_assets import Environment, Bundle

def register_assets(app):
	assets = Environment(app)
	assets.url = app.static_url_path
	assets.directory = app.static_folder
	assets.append_path('assets')
	scss = Bundle('scss/main.scss', filters='pyscss', output='main.css', depends=('scss/*.scss'))
	assets.register('scss_all', scss)