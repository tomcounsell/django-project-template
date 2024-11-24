# Dependency Setup with pip-tools

```bash
# Initial setup
pip install pip-tools
mkdir requirements
```

Create three files:
```txt
# requirements/base.in
Django==5.1.*
# Add core dependencies...

# requirements/dev.in
-r base.in
black
pytest
# Add dev tools...

# requirements/prod.in
-r base.in
# Add prod-specific deps...
```

```bash
# Generate locked files
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/prod.in -o requirements/prod.txt

# Install
pip install -r requirements/dev.txt  # For development
pip install -r requirements/prod.txt # For production

# Update all deps
pip-compile --upgrade requirements/*.in

# Update single package
pip-compile --upgrade-package package_name requirements/base.in
```

Commit both `.in` and `.txt` files.
