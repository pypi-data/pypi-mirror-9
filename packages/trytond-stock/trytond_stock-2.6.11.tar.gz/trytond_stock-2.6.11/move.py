#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
from functools import reduce
from trytond.model import ModelView, ModelSQL, fields
from trytond.backend import TableHandler
from trytond.pyson import In, Eval, Not, Equal, If, Get, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['Move']

STATES = {
    'readonly': In(Eval('state'), ['cancel', 'assigned', 'done']),
}
DEPENDS = ['state']


class Move(ModelSQL, ModelView):
    "Stock Move"
    __name__ = 'stock.move'
    _order_name = 'product'
    product = fields.Many2One("product.product", "Product", required=True,
        select=True, states=STATES,
        on_change=['product', 'currency', 'uom', 'company',
            'from_location', 'to_location'],
        domain=[('type', '!=', 'service')],
        depends=DEPENDS)
    product_uom_category = fields.Function(
        fields.Many2One('product.uom.category', 'Product Uom Category',
            on_change_with=['product']),
        'on_change_with_product_uom_category')
    uom = fields.Many2One("product.uom", "Uom", required=True, states=STATES,
        domain=[
            ('category', '=', Eval('product_uom_category')),
            ],
        on_change=['product', 'currency', 'uom', 'company',
            'from_location', 'to_location'],
        depends=['state', 'product_uom_category'])
    unit_digits = fields.Function(fields.Integer('Unit Digits',
        on_change_with=['uom']), 'on_change_with_unit_digits')
    quantity = fields.Float("Quantity", required=True,
        digits=(16, Eval('unit_digits', 2)), states=STATES,
        depends=['state', 'unit_digits'])
    internal_quantity = fields.Float('Internal Quantity', readonly=True,
        required=True)
    from_location = fields.Many2One("stock.location", "From Location",
        select=True, required=True, states=STATES, depends=DEPENDS,
        domain=[('type', 'not in', ('warehouse', 'view'))])
    to_location = fields.Many2One("stock.location", "To Location", select=True,
        required=True, states=STATES, depends=DEPENDS,
        domain=[('type', 'not in', ('warehouse', 'view'))])
    shipment_in = fields.Many2One('stock.shipment.in', 'Supplier Shipment',
        domain=[('company', '=', Eval('company'))], depends=['company'],
        readonly=True, select=True, ondelete='CASCADE')
    shipment_out = fields.Many2One('stock.shipment.out', 'Customer Shipment',
        domain=[('company', '=', Eval('company'))], depends=['company'],
        readonly=True, select=True, ondelete='CASCADE')
    shipment_out_return = fields.Many2One('stock.shipment.out.return',
        'Customer Return Shipment', readonly=True, select=True,
        domain=[('company', '=', Eval('company'))], depends=['company'],
        ondelete='CASCADE')
    shipment_in_return = fields.Many2One('stock.shipment.in.return',
        'Supplier Return Shipment', readonly=True, select=True,
        domain=[('company', '=', Eval('company'))], depends=['company'],
        ondelete='CASCADE')
    shipment_internal = fields.Many2One('stock.shipment.internal',
        'Internal Shipment', readonly=True, select=True, ondelete='CASCADE',
        domain=[('company', '=', Eval('company'))], depends=['company'])
    planned_date = fields.Date("Planned Date", states={
            'readonly': (In(Eval('state'), ['cancel', 'assigned', 'done'])
                | Eval('shipment_in') | Eval('shipment_out')
                | Eval('shipment_in_return') | Eval('shipment_out_return')
                | Eval('shipment_internal'))
            }, depends=['state', 'shipment_in', 'shipment_out',
            'shipment_in_return', 'shipment_out_return', 'shipment_internal'],
        select=True)
    effective_date = fields.Date("Effective Date", readonly=True, select=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
        ], 'State', select=True, readonly=True)
    company = fields.Many2One('company.company', 'Company', required=True,
        states={
            'readonly': Not(Equal(Eval('state'), 'draft')),
            },
        domain=[
            ('id', If(In('company', Eval('context', {})), '=', '!='),
                Get(Eval('context', {}), 'company', 0)),
            ],
        depends=['state'])
    unit_price = fields.Numeric('Unit Price', digits=(16, 4),
        states={
            'invisible': Not(Bool(Eval('unit_price_required'))),
            'required': Bool(Eval('unit_price_required')),
            'readonly': Not(Equal(Eval('state'), 'draft')),
            },
        depends=['unit_price_required', 'state'])
    cost_price = fields.Numeric('Cost Price', digits=(16, 4), readonly=True)
    currency = fields.Many2One('currency.currency', 'Currency',
        states={
            'invisible': Not(Bool(Eval('unit_price_required'))),
            'required': Bool(Eval('unit_price_required')),
            'readonly': Not(Equal(Eval('state'), 'draft')),
            },
        depends=['unit_price_required', 'state'])
    unit_price_required = fields.Function(fields.Boolean('Unit Price Required',
        on_change_with=['from_location', 'to_location']),
        'on_change_with_unit_price_required')

    @classmethod
    def __setup__(cls):
        super(Move, cls).__setup__()
        cls._sql_constraints += [
            ('check_move_qty_pos',
                'CHECK(quantity >= 0.0)', 'Move quantity must be positive'),
            ('check_move_internal_qty_pos',
                'CHECK(internal_quantity >= 0.0)',
                'Internal move quantity must be positive'),
            ('check_from_to_locations',
                'CHECK(from_location != to_location)',
                'Source and destination location must be different'),
            ('check_shipment',
                'CHECK((COALESCE(shipment_in, 0) / COALESCE(shipment_in, 1) ' \
                        '+ COALESCE(shipment_out, 0) / ' \
                            'COALESCE(shipment_out, 1) ' \
                        '+ COALESCE(shipment_internal, 0) / ' \
                            'COALESCE(shipment_internal, 1) ' \
                        '+ COALESCE(shipment_in_return, 0) / ' \
                            'COALESCE(shipment_in_return, 1) ' \
                        '+ COALESCE(shipment_out_return, 0) / ' \
                            'COALESCE(shipment_out_return, 1)) ' \
                        '<= 1)',
                'Move can be on only one Shipment'),
        ]
        cls._constraints += [
            ('check_period_closed', 'period_closed'),
        ]
        cls._order[0] = ('id', 'DESC')
        cls._error_messages.update({
            'set_state_draft': 'You can not set state to draft!',
            'set_state_assigned': 'You can not set state to assigned!',
            'set_state_done': 'You can not set state to done!',
            'del_draft_cancel': 'You can only delete draft ' \
                'or cancelled moves!',
            'period_closed': 'You can not modify move in closed period!',
            'modify_assigned_done_cancel': ('You can not modify a move '
                'in the state: "Assigned", "Done" or "Cancel"'),
            })

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor
        # Migration from 1.2: packing renamed into shipment
        table = TableHandler(cursor, cls, module_name)
        table.drop_constraint('check_packing')
        for suffix in ('in', 'out', 'in_return', 'out_return', 'internal'):
            old_column = 'packing_%s' % suffix
            new_column = 'shipment_%s' % suffix
            if table.column_exist(old_column):
                table.index_action(old_column, action='remove')
            table.drop_fk(old_column)
            table.column_rename(old_column, new_column)

        # Migration from 1.8: new field internal_quantity
        internal_quantity_exist = table.column_exist('internal_quantity')

        super(Move, cls).__register__(module_name)

        # Migration from 1.8: fill new field internal_quantity
        if not internal_quantity_exist:
            offset = 0
            limit = cursor.IN_MAX
            moves = True
            while moves:
                moves = cls.search([], offset=offset, limit=limit)
                offset += limit
                for move in moves:
                    internal_quantity = cls._get_internal_quantity(
                            move.quantity, move.uom, move.product)
                    cls.write([move], {
                        'internal_quantity': internal_quantity,
                        })
            table = TableHandler(cursor, cls, module_name)
            table.not_null_action('internal_quantity', action='add')

        # Migration from 1.0 check_packing_in_out has been removed
        table = TableHandler(cursor, cls, module_name)
        table.drop_constraint('check_packing_in_out')

        # Add index on create_date
        table.index_action('create_date', action='add')

    @staticmethod
    def default_planned_date():
        return Transaction().context.get('planned_date')

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_currency():
        Company = Pool().get('company.company')
        company = Transaction().context.get('company')
        if company:
            company = Company(company)
            return company.currency.id

    @staticmethod
    def default_unit_digits():
        return 2

    def on_change_with_unit_digits(self, name=None):
        if self.uom:
            return self.uom.digits
        return 2

    def on_change_product(self):
        pool = Pool()
        Uom = pool.get('product.uom')
        Currency = pool.get('currency.currency')

        res = {
            'unit_price': Decimal('0.0'),
            }
        if self.product:
            res['uom'] = self.product.default_uom.id
            res['uom.rec_name'] = self.product.default_uom.rec_name
            res['unit_digits'] = self.product.default_uom.digits
            unit_price = None
            if self.from_location and self.from_location.type in ('supplier',
                    'production'):
                unit_price = self.product.cost_price
            elif self.to_location and self.to_location.type == 'customer':
                unit_price = self.product.list_price
            if unit_price:
                if self.uom != self.product.default_uom:
                    unit_price = Uom.compute_price(self.product.default_uom,
                        unit_price, self.uom)
                if self.currency and self.company:
                    unit_price = Currency.compute(self.company.currency,
                        unit_price, self.currency, round=False)
                res['unit_price'] = unit_price
        return res

    def on_change_with_product_uom_category(self, name=None):
        if self.product:
            return self.product.default_uom_category.id

    def on_change_uom(self):
        pool = Pool()
        Uom = pool.get('product.uom')
        Currency = pool.get('currency.currency')

        res = {
            'unit_price': Decimal('0.0'),
            }
        if self.product:
            if self.to_location and self.to_location.type == 'storage':
                unit_price = self.product.cost_price
                if self.uom and self.uom != self.product.default_uom:
                    unit_price = Uom.compute_price(self.product.default_uom,
                        unit_price, self.uom)
                if self.currency and self.company:
                    unit_price = Currency.compute(self.company.currency,
                        unit_price, self.currency, round=False)
                res['unit_price'] = unit_price
        return res

    def on_change_with_unit_price_required(self, name=None):
        if (self.from_location
                and self.from_location.type in ('supplier', 'production')):
            return True
        if (self.to_location
                and self.to_location.type == 'customer'):
            return True
        if (self.from_location and self.to_location
                and self.from_location.type == 'storage'
                and self.to_location.type == 'supplier'):
            return True
        return False

    @classmethod
    def check_period_closed(cls, moves):
        Period = Pool().get('stock.period')
        periods = Period.search([
                ('state', '=', 'closed'),
                ], order=[('date', 'DESC')], limit=1)
        if periods:
            period, = periods
            for move in moves:
                date = (move.effective_date if move.effective_date
                    else move.planned_date)
                if date and date < period.date:
                    return False
        return True

    def get_rec_name(self, name):
        return ("%s%s %s"
            % (self.quantity, self.uom.symbol, self.product.rec_name))

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('product',) + tuple(clause[1:])]

    @classmethod
    def _update_product_cost_price(cls, product_id, quantity, uom, unit_price,
            currency, company, date):
        """
        Update the cost price on the given product.
        The quantity must be positive if incoming and negative if outgoing.
        The date is for the currency rate calculation.
        """
        pool = Pool()
        Uom = pool.get('product.uom')
        Product = pool.get('product.product')
        ProductTemplate = pool.get('product.template')
        Location = pool.get('stock.location')
        Currency = pool.get('currency.currency')
        Company = pool.get('company.company')
        Date = pool.get('ir.date')

        if isinstance(uom, (int, long)):
            uom = Uom(uom)
        if isinstance(currency, (int, long)):
            currency = Currency(currency)
        if isinstance(company, (int, long)):
            company = Company(company)

        context = {}
        locations = Location.search([
                ('type', '=', 'storage'),
                ])
        context['locations'] = [l.id for l in locations]
        context['stock_date_end'] = Date.today()
        with Transaction().set_context(context):
            product = Product(product_id)
        qty = Uom.compute_qty(uom, quantity, product.default_uom)

        qty = Decimal(str(qty))
        if hasattr(Product, 'cost_price'):
            product_qty = product.quantity
        else:
            product_qty = product.template.quantity
        product_qty = Decimal(str(product_qty))
        # convert wrt currency
        with Transaction().set_context(date=date):
            unit_price = Currency.compute(currency, unit_price,
                company.currency, round=False)
        # convert wrt to the uom
        unit_price = Uom.compute_price(uom, unit_price, product.default_uom)
        if product_qty + qty != Decimal('0.0'):
            new_cost_price = (
                (product.cost_price * product_qty) + (unit_price * qty)
                ) / (product_qty + qty)
        else:
            new_cost_price = product.cost_price

        if hasattr(Product, 'cost_price'):
            digits = Product.cost_price.digits
        else:
            digits = ProductTemplate.cost_price.digits
        new_cost_price = new_cost_price.quantize(
            Decimal(str(10.0 ** -digits[1])))

        with Transaction().set_user(0, set_context=True):
            Product.write([product], {
                    'cost_price': new_cost_price,
                    })

    @staticmethod
    def _get_internal_quantity(quantity, uom, product):
        Uom = Pool().get('product.uom')
        internal_quantity = Uom.compute_qty(uom, quantity,
            product.default_uom, round=True)
        return internal_quantity

    @classmethod
    def create(cls, vals):
        pool = Pool()
        Location = pool.get('stock.location')
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        Date = pool.get('ir.date')

        today = Date.today()
        vals = vals.copy()
        effective_date = vals.get('effective_date') or today

        product = Product(vals['product'])
        if vals.get('state') == 'done':
            vals['effective_date'] = effective_date
            currency_id = vals.get('currency', cls.default_currency())
            company_id = vals.get('company', cls.default_company())
            from_location = Location(vals['from_location'])
            to_location = Location(vals['to_location'])
            if (from_location.type in ('supplier', 'production')
                    and to_location.type == 'storage'
                    and product.cost_price_method == 'average'):
                cls._update_product_cost_price(vals['product'],
                        vals['quantity'], vals['uom'], vals['unit_price'],
                        currency_id, company_id, effective_date)
            if (to_location.type == 'supplier'
                    and from_location.type == 'storage'
                    and product.cost_price_method == 'average'):
                cls._update_product_cost_price(vals['product'],
                        -vals['quantity'], vals['uom'], vals['unit_price'],
                        currency_id, company_id, effective_date)
            if not vals.get('cost_price'):
                # Re-read product to get the updated cost_price
                product = Product(vals['product'])
                vals['cost_price'] = product.cost_price

        elif vals.get('state') == 'assigned':
            vals['effective_date'] = effective_date

        uom = Uom(vals['uom'])
        internal_quantity = cls._get_internal_quantity(vals['quantity'],
            uom, product)
        vals['internal_quantity'] = internal_quantity
        return super(Move, cls).create(vals)

    @classmethod
    def write(cls, moves, vals):
        Date = Pool().get('ir.date')

        today = Date.today()
        effective_date = vals.get('effective_date') or today

        if 'state' in vals:
            for move in moves:
                if vals['state'] == 'cancel':
                    vals['effective_date'] = None
                    if (move.from_location.type in ('supplier', 'production')
                            and move.to_location.type == 'storage'
                            and move.state != 'cancel'
                            and move.product.cost_price_method == 'average'):
                        cls._update_product_cost_price(move.product.id,
                                -move.quantity, move.uom, move.unit_price,
                                move.currency, move.company, today)
                    if (move.to_location.type == 'supplier'
                            and move.from_location.type == 'storage'
                            and move.state != 'cancel'
                            and move.product.cost_price_method == 'average'):
                        cls._update_product_cost_price(move.product.id,
                                move.quantity, move.uom, move.unit_price,
                                move.currency, move.company, today)

                elif vals['state'] == 'draft':
                    if move.state == 'done':
                        cls.raise_user_error('set_state_draft')
                elif vals['state'] == 'assigned':
                    if move.state in ('cancel', 'done'):
                        cls.raise_user_error('set_state_assigned')
                    vals['effective_date'] = effective_date
                elif vals['state'] == 'done':
                    if move.state in ('cancel'):
                        cls.raise_user_error('set_state_done')
                    vals['effective_date'] = effective_date

                    if (move.from_location.type in ('supplier', 'production')
                            and move.to_location.type == 'storage'
                            and move.state != 'done'
                            and move.product.cost_price_method == 'average'):
                        cls._update_product_cost_price(move.product.id,
                                move.quantity, move.uom, move.unit_price,
                                move.currency, move.company, effective_date)
                    if (move.to_location.type == 'supplier'
                            and move.from_location.type == 'storage'
                            and move.state != 'done'
                            and move.product.cost_price_method == 'average'):
                        cls._update_product_cost_price(move.product.id,
                                -move.quantity, move.uom, move.unit_price,
                                move.currency, move.company, effective_date)

        if reduce(lambda x, y: x or y in vals, ('product', 'uom', 'quantity',
                'from_location', 'to_location', 'company', 'unit_price',
                'currency'), False):
            for move in moves:
                if move.state in ('assigned', 'done', 'cancel'):
                    cls.raise_user_error('modify_assigned_done_cancel')
        if reduce(lambda x, y: x or y in vals,
                ('planned_date', 'effective_date'), False):
            for move in moves:
                if move.state in ('done', 'cancel'):
                    cls.raise_user_error('modify_assigned_done_cancel')

        super(Move, cls).write(moves, vals)

        if vals.get('state', '') == 'done':
            for move in moves:
                if not move.cost_price:
                    cls.write([move], {
                            'cost_price': move.product.cost_price,
                            })

        for move in moves:
            internal_quantity = cls._get_internal_quantity(move.quantity,
                    move.uom, move.product)
            if internal_quantity != move.internal_quantity:
                # Use super to avoid infinite loop
                super(Move, cls).write([move], {
                        'internal_quantity': internal_quantity,
                        })

    @classmethod
    def delete(cls, moves):
        for move in moves:
            if move.state not in  ('draft', 'cancel'):
                cls.raise_user_error('del_draft_cancel')
        super(Move, cls).delete(moves)

    def pick_product(self, location_quantities):
        """
        Pick the product across the location. Naive (fast) implementation.
        Return a list of tuple (location, quantity) for quantities that can be
        picked.
        """
        to_pick = []
        needed_qty = self.quantity
        for location, available_qty in location_quantities.iteritems():
            # Ignore available_qty when too small
            if available_qty < self.uom.rounding:
                continue
            if needed_qty <= available_qty:
                to_pick.append((location, needed_qty))
                return to_pick
            else:
                to_pick.append((location, available_qty))
                needed_qty -= available_qty
        # Force assignation for consumables:
        if self.product.consumable:
            to_pick.append((self.from_location, needed_qty))
            return to_pick
        return to_pick

    @classmethod
    def assign_try(cls, moves):
        '''
        Try to assign moves.
        It will split the moves to assign as much possible.
        Return True if succeed or False if not.
        '''
        pool = Pool()
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        Date = pool.get('ir.date')
        Location = pool.get('stock.location')

        Transaction().cursor.lock(cls._table)

        locations = Location.search([
                ('parent', 'child_of', [x.from_location.id for x in moves]),
                ])
        with Transaction().set_context(
                stock_date_end=Date.today(),
                stock_assign=True):
            pbl = Product.products_by_location(
                location_ids=[l.id for l in locations],
                product_ids=[m.product.id for m in moves])

        success = True
        for move in moves:
            if move.state != 'draft':
                continue
            to_location = move.to_location
            location_qties = {}
            childs = Location.search([
                    ('parent', 'child_of', [move.from_location.id]),
                    ])
            for location in childs:
                if (location.id, move.product.id) in pbl:
                    location_qties[location] = Uom.compute_qty(
                            move.product.default_uom,
                            pbl[(location.id, move.product.id)], move.uom,
                            round=False)

            to_pick = move.pick_product(location_qties)

            picked_qties = 0.0
            for _, qty in to_pick:
                picked_qties += qty

            if picked_qties < move.quantity:
                success = False
                first = False
                cls.write([move], {
                    'quantity': move.quantity - picked_qties,
                    })
            else:
                first = True
            for from_location, qty in to_pick:
                values = {
                    'from_location': from_location.id,
                    'quantity': qty,
                    'state': 'assigned',
                    }
                if first:
                    cls.write([move], values)
                    first = False
                else:
                    cls.copy([move], default=values)

                qty_default_uom = Uom.compute_qty(move.uom, qty,
                        move.product.default_uom, round=False)

                pbl[(from_location.id, move.product.id)] = (
                    pbl.get((from_location.id, move.product.id), 0.0)
                    - qty_default_uom)
                pbl[(to_location.id, move.product.id)] = (
                    pbl.get((to_location.id, move.product.id), 0.0)
                    + qty_default_uom)
        return success
