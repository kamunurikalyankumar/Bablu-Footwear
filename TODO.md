# Project Restructuring TODO

## Steps to Restructure Folders into Standard Flask Layout

- [x] Create app/ directory at root level
- [x] Create app/routes/ subdirectory
- [x] Create app/templates/ subdirectory
- [x] Create app/static/ subdirectory
- [x] Move routes/ directory contents to app/routes/
- [x] Move models.py to app/models.py
- [x] Move all .html files (about.html, admin.html, contact.html, index.html, login.html, register.html, shop-single.html, shop.html) to app/templates/
- [x] Move assets/ directory to app/static/ (rename assets to static)
- [x] Create app/__init__.py with Flask app initialization code from app.py
- [x] Update app.py to be a run script that imports and runs the app from app package
- [x] Update import statements in routes/*.py to import from app.models instead of models
- [x] Update Flask app configuration for template_folder and static_folder to point to app/templates and app/static
- [x] Update any hardcoded paths in the code for new structure
- [x] Test the restructured application to ensure it runs correctly
- [x] Remove old directories and files if no longer needed (e.g., empty routes/ at root)
