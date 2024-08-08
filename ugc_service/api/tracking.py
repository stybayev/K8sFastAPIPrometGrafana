from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)


@api.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint returning a list of colors by palette
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          id: Palette
          type: object
          properties:
            palette_name:
              type: array
              items:
                schema:
                  id: Color
                  type: string
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cyan', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)
