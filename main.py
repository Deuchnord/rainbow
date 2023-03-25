import re

from hashlib import sha1
from flask import Flask, request, redirect, url_for, render_template

# Used on index page only
from random import randint

app = Flask(__name__)

VOWELS = 'aeiou'


def name_color(code: str):
    reg_digit = re.compile('[0-9]')
    reg_accepting_vowel = re.compile(f'[^{VOWELS}]')
    reg_two_successive_vowels = re.compile(f'[{VOWELS}]{{2}}')

    name = ""
    hashed = sha1(code.lower().encode()).hexdigest()
    adder = 0

    for c in hashed:
        if len(name) == 6:
            break

        if reg_digit.match(c):
            adder += int(c)
            continue

        if name != "" and reg_accepting_vowel.match(name[-1]):
            name += VOWELS[adder % len(VOWELS)]
            adder = 0
            continue

        nc = (ord(c) + adder)
        if chr(nc) in VOWELS and len(name) >= 2 and reg_two_successive_vowels.match(name[-2:]):
            adder += 1
            nc = ord(c) + adder

        if nc > ord('z'):
            nc = ord('z')

        name += chr(nc)
        adder = 0

    # Cheat a little by replacing any "qu" with "ku" to prevent pronunciation issues
    return name.replace('qu', 'ku')


@app.route("/")
def index(error: bool = False):
    r, v, b = hex(randint(0, 255))[2:], hex(randint(0, 255))[2:], hex(randint(0, 255))[2:]
    random_color = f"{r}{v}{b}"

    return render_template("index.html", random_color=random_color, error=error)


@app.route("/name-this", methods=["POST"])
def name_this():
    colorhex = request.form.get("color").replace("#", "")
    return redirect(url_for("color", colorhex=colorhex))


@app.route("/<colorhex>")
def color(colorhex: str):

    if not re.match("[0-9a-f]{6}", colorhex.lower()):
        return index(error=True), 404

    return render_template(
        "color.html",
        colorhex=colorhex,
        colorname=name_color(colorhex).capitalize(),
        text_color=get_text_color(colorhex)
    )


def get_text_color(bghex: str):
    text_color = "363636"
    r, g, b = int(text_color[0:1], 16), int(text_color[2:3], 16), int(text_color[4:5], 16)
    luminance_text = 0.2126 * r + 0.7152 * g + 0.0722 * b

    r, g, b = int(bghex[0:1], 16), int(bghex[2:3], 16), int(bghex[4:5], 16)
    luminance_bg = 0.2126 * r + 0.7152 * g + 0.0722 * b

    contrast = (luminance_bg + 0.05) / (luminance_text + 0.05)

    if contrast < 3:
        return "eeeeee"

    return text_color


if __name__ == '__main__':
    app.run(port=8080)
