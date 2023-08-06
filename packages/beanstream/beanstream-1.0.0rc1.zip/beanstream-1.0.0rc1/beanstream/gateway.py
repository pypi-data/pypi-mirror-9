'''
Copyright 2012 Upverter Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from beanstream import errors, payment_profiles, process_transaction, recurring_billing, reports

class Beanstream(object):

    def __init__(self, **options):
        """ Initialize the gateway.

        Keyword arguments:
            require_cvd: True to enable; default disabled.
            require_billing_address: True to enable; default disabled.
        """

        self.REQUIRE_CVD = options.get('require_cvd', False)
        self.REQUIRE_BILLING_ADDRESS = options.get('require_billing_address', False)

        self.merchant_id = None
        self.login_company = None
        self.payment_passcode = None
        self.payment_profile_passcode = None
        self.reporting_passcode = None

        #error testing
        self.testErrorGenerator = None

    def configure(self, merchant_id, **params):
        """ Configure the gateway.
        """
        self.merchant_id = merchant_id
        self.payment_passcode = params.get('payment_passcode', None)
        self.payment_profile_passcode = params.get('payment_profile_passcode', None)
        self.recurring_billing_passcode = params.get('recurring_billing_passcode', None)
        self.reporting_passcode = params.get('reporting_passcode', None)

    '''not required, used for TESTING by generating errors on every transaction
    '''
    def setTestErrorGenerator(self, errorGenerator):
        self.testErrorGenerator = errorGenerator
        
     
    def purchase(self, amount, card, billing_address=None):
        """ Returns a Purchase object with the specified options.
        """
        txn = process_transaction.Purchase(self, amount)
        txn.set_card(card)
        if billing_address:
            txn.set_billing_address(billing_address)

        return txn

    def void_purchase(self, transaction_id, amount):
        """ Returns an Adjustment object configured for voiding the specified
        transaction for the specified amount.
        """
        txn = process_transaction.Adjustment(self, process_transaction.Adjustment.VOID, transaction_id, amount)
        return txn

    def return_purchase(self, transaction_id, amount):
        """ Returns an Adjustment object configured for returning the specified
        transaction for the specified amount.
        """
        txn = process_transaction.Adjustment(self, process_transaction.Adjustment.RETURN, transaction_id, amount)
        return txn

    def void_return(self, transaction_id, amount):
        """ Returns an Adjustment object configured for voiding the return of
        the specified transaction for the specified amount.
        """
        txn = process_transaction.Adjustment(self, process_transaction.Adjustment.VOID_RETURN, transaction_id, amount)
        return txn

    def preauth(self, amount, card, billing_address=None):
        """ Returns a PreAuthorization object with the specified options.
        """
        txn = process_transaction.PreAuthorization(self, amount)
        txn.set_card(card)
        if billing_address:
            txn.set_billing_address(billing_address)

        return txn

    def preauth_completion(self, transaction_id, amount):
        """ Returns an Adjustment object configured for completing the
        preauthorized transaction for the specified amount.
        """
        txn = process_transaction.Adjustment(self, process_transaction.Adjustment.PREAUTH_COMPLETION, transaction_id, amount)
        return txn

    def cancel_preauth(self, transaction_id):
        """ Returns an Adjustment object configured for cancelling the
        preauthorized transaction.
        """
        txn = process_transaction.Adjustment(self, process_transaction.Adjustment.PREAUTH_COMPLETION, transaction_id, 0)
        return txn

    def create_payment_profile(self, card, billing_address=None):
        """ Returns a CreatePaymentProfile object with the specified options.
        """
        txn = payment_profiles.CreatePaymentProfile(self, card)
        if billing_address:
            txn.set_billing_address(billing_address)

        return txn

    def modify_payment_profile(self, customer_code):
        """ Returns a ModifyPaymentProfile object with the specified options.
        """
        txn = payment_profiles.ModifyPaymentProfile(self, customer_code)
        return txn

    def get_payment_profile(self, customer_code):
        """ Returns a GetPaymentProfile object with the specified options.
        """
        txn = payment_profiles.GetPaymentProfile(self, customer_code)
        return txn

    def purchase_with_payment_profile(self, amount, customer_code):
        """ Returns a Purchase object with the specified options.
        """
        txn = process_transaction.Purchase(self, amount)
        txn.set_customer_code(customer_code)
        return txn

    def preauth_with_payment_profile(self, amount, customer_code):
        """ Returns a PreAuthorization object with the specified options.
        """
        txn = process_transaction.PreAuthorization(self, amount)
        txn.set_customer_code(customer_code)
        return txn

    def create_recurring_billing_account_from_payment_profile(self, amount,
            customer_code, frequency_period, frequency_increment):
        """ Returns a CreateRecurringBillingAccount object with the specified
        options.
        """
        txn = recurring_billing.CreateRecurringBillingAccount(self, amount,
                frequency_period, frequency_increment)
        txn.set_customer_code(customer_code)
        return txn

    def create_recurring_billing_account(self, amount, card, frequency_period,
            frequency_increment, billing_address=None):
        """ Returns a CreateRecurringBillingAccount object with the specified
        options.
        """
        txn = recurring_billing.CreateRecurringBillingAccount(self, amount,
                frequency_period, frequency_increment)
        txn.set_card(card)
        if billing_address:
            txn.set_billing_address(billing_address)

        return txn

    def modify_recurring_billing_account(self, account_id):
        """ Returns a ModifyRecurringBillingAccount object with the specified
        options.
        """
        txn = recurring_billing.ModifyRecurringBillingAccount(self, account_id)
        return txn

    def query_transactions(self):
        """ Query for transactions with many different criteria.
            Set the criteria with set_query_params() or set_query_params_criteria()
        """
        txn = reports.TransactionReport(self)
        txn.use_reports_api()
        return txn

    def get_transaction(self, transId):
        """ Query for transactions with many different criteria.
            Set the criteria with set_query_params() or set_query_params_criteria()
        """
        txn = reports.GetTransaction(self)
        txn.use_payments_api()
        txn.set_transaction_id(transId)
        return txn


