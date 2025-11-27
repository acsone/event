# Copyright 2019 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from typing import Self

from odoo.orm.types import ValuesType

from odoo import fields, models

class EventQuestion(models.Model):
    _inherit = "event.question"

    restricted_ticket_ids = fields.Many2many(
        comodel_name="event.event.ticket",
        string="Limited to tickets",
        domain="[('event_id', '=', parent.id)]",
        ondelete="restrict",
    )

    def create(self, vals_list: list[ValuesType]) -> Self:
        return super().create(vals_list)
