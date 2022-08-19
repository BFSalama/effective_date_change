from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_quant import StockQuant
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import groupby


class InventoryAdjustmentDate(models.Model):
    _inherit = 'stock.quant'

    def _apply_inventory(self):
        res = super(StockQuant, self)
        move_vals = []
        custom_date = self.accounting_date
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(quant.inventory_diff_quantity,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     quant.location_id))
            else:
                move_vals.append(
                    quant._get_inventory_move_values(-quant.inventory_diff_quantity,
                                                     quant.location_id,
                                                     quant.product_id.with_company(quant.company_id).property_stock_inventory,
                                                     out=True))
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves.with_context(force_period_date=custom_date)._action_done()
        self.location_id.write({'last_inventory_date': quant.accounting_date})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            # quant.date = quant.accounting_date
            quant.inventory_date = date_by_location[quant.location_id]
        move = self.env['stock.move'].search([('id', '=', moves.id)])
        move.date = custom_date
        for move_lines in move.move_line_ids:
            move_lines.date = quant.accounting_date
        self.write({'inventory_quantity': 0, 'user_id': False})
        self.write({'inventory_diff_quantity': 0})
        self.write({'accounting_date': 0})
        return res