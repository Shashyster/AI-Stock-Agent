# Design backup – original “jazzy” style

This folder holds a copy of the **previous design** (gradient header, jazzy buttons, glow effects, Outfit font) so you can revert at any time.

## How to revert to this design

1. Copy the files from this folder **over** the current ones:
   - `style.css` → `static/style.css`
   - `index.html` → `templates/index.html`
2. In `templates/index.html`, change the CSS link to use a new version so the browser doesn’t use cached CSS, e.g. `?v=revert` or `?v=4`.
3. Restart your app / redeploy if needed.

You can also open these files side-by-side with the current ones to copy specific sections back.
