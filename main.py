"""GovHack 2016

';-- -
Matthew Alger
Mitchell Busby
"""

from flask import Flask

from govhack import app

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
