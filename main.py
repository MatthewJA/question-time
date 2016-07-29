"""GovHack 2016

';-- -
Matthew Alger
Mitchell Busby
"""

import os


from flask import Flask
from govhack import app

if __name__ == '__main__':
    app.run('0.0.0.0', port=int(os.environ.get('PORT', 5000)))
