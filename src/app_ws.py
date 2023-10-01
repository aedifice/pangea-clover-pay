import os
from flask import (
    Flask, render_template, request, redirect, session, url_for
)
from app_lib import charge_request, decrypt_saved_card


app = Flask(__name__)

# main route: provide an ecommerce form and collect card details on submit
@app.route("/", methods=("GET", "POST"))
def ecomm():
    if request.method == "POST":
        # form was submitted; retrieve values from all required fields
        amount = request.form["amount"]
        card = request.form["card"]
        expiration = request.form["expiration"]
        cvv = request.form["cvv"]
        zipcode = request.form["zipcode"]

        # see if the "save card" checkbox was checked
        save = False
        if request.form.get("save"):
            save = True

        # attempt the transaction and redirect based on success or failure
        result_success = charge_request(amount, card, expiration, cvv, zipcode, save)

        if result_success:
            return redirect(url_for("thanks", amount=amount))
        else:
            return redirect(url_for("error"))

    # if we've saved a card in the session, use those details to prefill the form
    savedCard = {"card": "", "expiration": "", "cvv": "", "zipcode": ""}
    if "card" in session:
        savedCard = decrypt_saved_card()

    return render_template("/ecomm.html", savedCard=savedCard)


# payment success route
@app.route("/thank-you")
def thanks():
    amount = request.args.get("amount")
    return render_template("/thank-you.html", amount=amount)


# payment failure route
@app.route("/error")
def error():
    return render_template("pay-error.html")


# set up and run the Flask app
if __name__ == "__main__":
    app.secret_key = os.getenv("FLASK_SECRET")
    app.run(host="0.0.0.0", port="3000")
