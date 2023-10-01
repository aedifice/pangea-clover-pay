# Pangea-Clover Pay

This app demonstrates a [Clover](https://www.clover.com/) ecommerce solution with [Pangea](https://pangea.cloud/) security features. Amount and card details are submitted via a form and routed to Clover to process the transaction.

The form offers an option to save the card to reuse later. When checked, card details are encrypted using Pangea and saved to the user session. When the form is visited again later, saved card details are decrypted and used to prefill the form.

The demo also makes use of Pangea's secure audit log to save transaction details (amount, last 4 digits of the card, and success/failure). Logs can be reviewed for suspicious activity or total transaction amounts.

The demo is written in Python using the Flask framework for a quick way to get up and running. Docker is also used for ease of portability.

## Setup

Both a Pangea account and a Clover developer account (with a test app and merchant) are required to run this demo. The app also uses [Docker](https://www.docker.com/) for simple environment configuration and portability. See the documentation of each site for more details.

Specifically for this demo, you will need to add values to the variables in `app.env.template` and save it to an `app.env` file. Required environment variables are:
* `FLASK_SECRET`: a unique secret that Flask will use to set up the session
* `PANGEA_DOMAIN`: base URL for your Pangea project, based on selected cloud provider
* `PANGEA_AUDIT_TOKEN`: authorization token for Pangea audit functionality
* `PANGEA_VAULT_TOKEN`: authorization token for Pangea vault (we use it for encryption) functionality
* `CLOVER_ACCESS_TOKEN`: authorization token for Clover functionality; specific to an app and a merchant
* `CLOVER_PAKMS`: merchant-specific API key for Clover ecommerce
* `CLOVER_MODULUS`: merchant-specific modulus to construct an RSA key for encryption; this and following values can be retrieved from `/v2/merchant/{mId}/pay/key`
* `CLOVER_EXPONENT`: merchant-specific exponent to construct an RSA key
* `CLOVER_PREFIX`: merchant-specific value that is prepended to a card number during encryption

With the environment properly configured, build and run the app using:
`docker compose up`

You can then visit the sample app at `localhost:3000`

## Future features

This demo was made in about a day and is not fully featured! It should not be used as-is to take live payments. Below are possible options to improve the demo for future.

### Pangea

* Make use of IP Intel to geolocate where payments are coming from and check for suspicious or malicious reputation. Results can be added to the audit log or preempt the transaction attempt if activity seems too suspicious.
* If certain IP locations should be blocked entirely, the Embargo feature may help.

### Clover

* Make app more extensible. Currently, merchant-specific details are hardcoded as part of the environment. To make the app usable by multiple merchants, it should be able to authenticate the merchant-app connection with OAuth and retrieve PAKMS and encryption keys programmatically. Perhaps Pangea's AuthN feature could help with authenticating and managing users?

### Misc.

* Add validation to form input (including handling payment amounts properly)! Though as-is, it makes it easy to test the payment failure flow...
* Exception handling and more unhappy-path handling in general.
* Make UI prettier.
