from flask import render_template
from api.app import app, db, cache
from configuration.config import ConfigManager


@app.route('/ansible-wrapper-configuration')
def ansible_configuration():
    cm = ConfigManager()
    print(cm.inventory)
    return render_template('ansible_config_dashboard.html', inventory=cm.inventory)

@app.route('/ansible-dashboard')
def ansible_dashboard():
    cm = ConfigManager()
    print(cm.inventory)
    return render_template('empty.html')