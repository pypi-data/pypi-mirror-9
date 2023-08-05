# -*- coding: utf-8 -*-
"""
    party.py

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime

from trytond.pool import PoolMeta, Pool
from nereid import route, login_required, render_template, request, \
    current_user, redirect, url_for, flash, jsonify, abort
from flask_wtf import Form
from wtforms import TextField, validators, \
    ValidationError, SelectField, IntegerField
from trytond.error import UserError
from nereid.contrib.locale import make_lazy_gettext

__metaclass__ = PoolMeta
__all__ = ['Party', 'PaymentProfile']
_ = make_lazy_gettext('nereid_payment_gateway')


class PaymentProfileForm(Form):
    address = IntegerField([validators.Required()])
    owner = TextField('Full Name on Card', [validators.Required(), ])
    number = TextField(
        'Card Number', [validators.Required(), validators.Length(max=20)]
    )
    expiry_month = SelectField(
        'Card Expiry Month',
        [validators.Required(), validators.Length(min=2, max=2)],
        choices=[
            ('01', _('01-January')),
            ('02', _('02-February')),
            ('03', _('03-March')),
            ('04', _('04-April')),
            ('05', _('05-May')),
            ('06', _('06-June')),
            ('07', _('07-July')),
            ('08', _('08-August')),
            ('09', _('09-September')),
            ('10', _('10-October')),
            ('11', _('11-November')),
            ('12', _('12-December')),
        ]
    )

    current_year = datetime.utcnow().date().year
    year_range = (current_year, current_year + 25)
    expiry_year = SelectField(
        'Card Expiry Year',
        [validators.Required(), validators.NumberRange(*year_range)],
        coerce=int,
    )
    cvv = TextField(
        'CVD/CVV Number',
        [validators.Required(), validators.Length(min=3, max=4)]
    )

    def __init__(self, *args, **kwargs):
        super(PaymentProfileForm, self).__init__(*args, **kwargs)

        # Set the expiry year values
        self.expiry_year.choices = [
            (year, year) for year in range(*self.year_range)
        ]

    def validate_address(form, field):
        """
        Validate address selected by user.
        """
        Address = Pool().get('party.address')
        addresses = Address.search([
            ('party', '=', current_user.party.id),
            ('id', '=', field.data),
        ], limit=1)
        if not addresses:
            raise ValidationError('Address you selected is not valid.')


class Party:
    __name__ = 'party.party'

    @classmethod
    @route('/my-cards', methods=['GET'])
    @login_required
    def view_payment_profiles(cls):
        """
        Render all the cards available in user account.
        """

        if request.is_xhr:
            return jsonify(
                payment_profile=[
                    profile.serialize()
                    for profile in current_user.party.payment_profiles
                ]
            )
        return render_template('my-cards.jinja')

    @classmethod
    @route('/my-cards/add-card', methods=['GET', 'POST'])
    @login_required
    def nereid_add_payment_profile(cls):
        """
        Add card to user profile.
        """
        AddPaymentProfileWizard = Pool().get(
            'party.party.payment_profile.add', type='wizard'
        )
        Address = Pool().get('party.address')

        gateway = request.nereid_website.credit_card_gateway
        form = PaymentProfileForm()

        if form.validate_on_submit():
            profile_wiz = AddPaymentProfileWizard(
                AddPaymentProfileWizard.create()[0]
            )
            profile_wiz.card_info.party = current_user.party
            profile_wiz.card_info.address = Address(form.address.data)
            profile_wiz.card_info.provider = gateway.provider
            profile_wiz.card_info.gateway = gateway
            profile_wiz.card_info.owner = form.owner.data
            profile_wiz.card_info.number = form.number.data
            profile_wiz.card_info.expiry_month = form.expiry_month.data
            profile_wiz.card_info.expiry_year = \
                unicode(form.expiry_year.data)
            profile_wiz.card_info.csc = form.cvv.data

            try:
                profile_wiz.transition_add()
                flash(_('Credit Card added successfully!'))
            except UserError, e:  # pragma: no cover
                flash(_(e.message))
            finally:
                if request.is_xhr:
                    return 'success', 200
                return redirect(url_for('party.party.view_payment_profiles'))
        return render_template('add-card.jinja', form=form)

    @classmethod
    @route("/my-cards/remove-card", methods=["POST"])
    @login_required
    def remove_payment_profile(cls):
        """
        Make payment profile inactive if user removes the credit card.
        """
        PaymentProfile = Pool().get('party.payment_profile')

        profiles = PaymentProfile.search([
            ('id', '=', request.form['profile_id']),
            ('party', '=', current_user.party.id),
        ])
        if not profiles:
            abort(403)

        payment_profile, = profiles
        payment_profile.active = False
        payment_profile.save()
        if request.is_xhr:
            return 'success', 200

        flash(_('Payment Profile has been deleted successfully!'))
        return redirect(request.referrer)


class PaymentProfile:
    __name__ = 'party.payment_profile'

    def serialize(self, purpose=None):
        """
        Serialize payment profile data
        """
        return {
            'id': self.id,
            'last_4_digits': self.last_4_digits,
            'owner': self.party.rec_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
        }
