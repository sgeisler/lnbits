from requests import get, post
from os import getenv
from .base import InvoiceResponse, PaymentResponse, PaymentStatus, Wallet

class LnbitsWallet(Wallet):

    def __init__(self):
        self.endpoint = getenv("LNBITS_ENDPOINT")
        self.auth_admin = getenv("LNBITS_ADMIN_MACAROON")
        self.auth_invoice = getenv("LNBITS_INVOICE_MACAROON")

    def create_invoice(self, amount: int, memo: str = "") -> InvoiceResponse:
        r = post(
            url=f"{self.endpoint}/api/v1/payments",
            headers=self.auth_invoice,
            json={"out": False, "amount": amount, "memo": memo}
        )
        ok, checking_id, payment_request, error_message = r.ok, None, None, None

        if r.ok:
            data = r.json()
            checking_id, payment_request = data["checking_id"], data["payment_request"]
        else:
            error_message = r.json()["message"]
        return InvoiceResponse(ok, checking_id, payment_request, error_message)

    def pay_invoice(self, bolt11: str) -> PaymentResponse:
        r = post(
            url=f"{self.endpoint}/api/v1/payments",
            headers=self.auth_admin,
            json={"out": True, "bolt11": bolt11}
        )
        ok, checking_id, fee_msat, error_message = True, None, 0, None

        if r.ok:
            data = r.json()
            checking_id = data["checking_id"]
        else:
            error_message = r.json()["message"]
        return InvoiceResponse(ok, checking_id, fee_msat, error_message)

    def get_invoice_status(self, checking_id: str) -> PaymentStatus:
        r = get(url=f"{self.endpoint}/api/v1/payments/{checking_id}", headers=self.auth_invoice)
        return PaymentStatus(r['paid'])

    def get_payment_status(self, checking_id: str) -> PaymentStatus:
        r = get(url=f"{self.endpoint}/api/v1/payments/{checking_id}", headers=self.auth_invoice)
        return PaymentStatus(r['paid'])
