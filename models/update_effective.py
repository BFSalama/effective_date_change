from odoo import models


class UpdateEffective(models.Model):
    _inherit = "stock.picking"

    def wiz_open(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'change.effective.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
    # SilkSoft addition


class UpdateEffectiveManufacturing(models.Model):
    _inherit = "mrp.production"

    def wizard_open(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'change.effective.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
