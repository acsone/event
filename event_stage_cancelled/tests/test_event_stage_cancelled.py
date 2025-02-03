# Copyright 2024 Tecnativa S.L. - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.base.tests.common import BaseCommon


class TestEventCancelCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create(
            {
                "date_begin": "2024-05-06 09:00:00",
                "date_end": "2024-05-08 18:00:00",
                "name": "OCA DAYS",
            }
        )
        # Let's prevent default schedulers that could distort our test case
        cls.event.event_mail_ids.unlink()
        cls.mail_template = cls.env["mail.template"].create(
            {
                "name": "Test event cancelled",
                "model_id": cls.env.ref("event.model_event_registration").id,
                # Just a test, the event will go perfectly. Join it!
                "subject": "The event is cancelled!",
                "body_html": "<p>We're sorry to announce that...</p>",
            }
        )
        cls.event_mail = cls.env["event.mail"].create(
            [
                {
                    "event_id": cls.event.id,
                    "notification_type": "mail",
                    "interval_unit": "now",
                    "interval_type": "after_cancel",
                    "template_ref": f"mail.template, {cls.mail_template.id}",
                }
            ]
        )
        cls.attendees = cls.env["event.registration"].create(
            [
                {
                    "event_id": cls.event.id,
                    "name": f"Test attendee {reg}",
                    "email": f"test_attendee_{reg}@test.com",
                }
                for reg in range(5)
            ]
        )
        (
            cls.attendee_1,
            cls.attendee_2,
            cls.attendee_3,
            cls.attendee_4,
            cls.attendee_5,
        ) = cls.attendees
        # Let's add some variations
        (cls.attendee_1 + cls.attendee_2).state = "draft"
        (cls.attendee_3 + cls.attendee_4).state = "open"
        cls.attendee_5.state = "cancel"

    def test_event_cancellation(self):
        """Test the processes triggered by the event cancellation"""
        # First cancel the event/registrations
        self.event.button_cancel()

        # Initial execution
        self.event_mail.execute()

        # Check attendee cancellation states
        cancelled_attendees = self.attendees.filtered(lambda a: a.state == "cancel")
        self.assertEqual(
            len(cancelled_attendees),
            len(self.attendees),
            f"Expected all attendees to be cancelled. Current states: "
            f"{', '.join(f'{a.name}: {a.state}' for a in self.attendees)}",
        )

        # Verify cancelled_from_event flag
        cancelled_from_event = self.attendees.filtered("cancelled_from_event")
        self.assertEqual(
            len(cancelled_from_event),
            4,
            f"Expected 4 attendees marked as "
            f"cancelled_from_event, got {len(cancelled_from_event)}",
        )

        # Verify notification recipients
        expected_recipients = (
            self.attendee_1 + self.attendee_2 + self.attendee_3 + self.attendee_4
        )
        actual_recipients = self.event_mail.mail_registration_ids.registration_id
        self.assertEqual(
            actual_recipients,
            expected_recipients,
            "Mismatch in notification recipients",
        )

        # Verify mail state
        self.assertEqual(
            self.event_mail.mail_state,
            "sent",
            "Mail state should be 'sent' after execution",
        )

        # Verify all notifications were sent
        unsent_mails = self.event_mail.mail_registration_ids.filtered(
            lambda r: not r.mail_sent
        )
        self.assertFalse(
            unsent_mails,
            f"All mail registrations should be "
            f"marked as sent. Unsent: {len(unsent_mails)}",
        )

    def test_compute_show_cancel_button(self):
        """Test the computation of the show_cancel_button field."""
        # Ensure no cancel stage exists
        self.env["event.stage"].search([("is_cancelled", "=", True)]).unlink()
        self.event._compute_show_cancel_button()

        # No cancel stage should result in False
        self.assertFalse(
            self.event.show_cancel_button,
            "show_cancel_button should be False when no cancel stage exists.",
        )

        # Create a cancel stage
        cancel_stage = self.env["event.stage"].create(
            {"name": "Cancelled", "is_cancelled": True}
        )
        open_stage = self.env["event.stage"].create(
            {"name": "Open", "is_cancelled": False}
        )

        # Assign a non-cancel stage and check show_cancel_button
        self.event.stage_id = open_stage
        self.event._compute_show_cancel_button()
        self.assertTrue(
            self.event.show_cancel_button,
            "show_cancel_button should be True when a cancel "
            "stage exists and event is not done.",
        )

        # Assign a cancel stage and check show_cancel_button
        self.event.stage_id = cancel_stage
        self.event._compute_show_cancel_button()
        self.assertFalse(
            self.event.show_cancel_button,
            "show_cancel_button should be False when the event is already cancelled.",
        )

        # Event is done
        open_stage.write({"pipe_end": True})
        self.event.stage_id = open_stage
        self.event._compute_show_cancel_button()
        self.assertFalse(
            self.event.show_cancel_button,
            "show_cancel_button should be False when the event is done.",
        )

    def test_compute_scheduled_date(self):
        """Test the scheduled date computation for after_cancel interval type."""
        # Set event stage to cancelled
        cancel_stage = self.env["event.stage"].create(
            {"name": "Cancelled", "is_cancelled": True}
        )
        self.event.stage_id = cancel_stage

        # Check scheduled_date computation
        self.event_mail._compute_scheduled_date()
        self.assertTrue(self.event_mail.scheduled_date)

    def test_execute_cancelled_registrations(self):
        """Test that the execute method works for cancelled registrations."""
        # Set event stage to cancelled and execute
        cancel_stage = self.env["event.stage"].create(
            {"name": "Cancelled", "is_cancelled": True}
        )
        self.event.stage_id = cancel_stage
        self.event.button_cancel()

        # Ensure cancelled registrations are correctly handled
        self.event_mail.execute()
        cancelled_attendees = self.attendees.filtered("cancelled_from_event")
        self.assertEqual(
            set(self.event_mail.mail_registration_ids.mapped("registration_id.id")),
            set(cancelled_attendees.ids),
        )
        self.assertTrue(all(self.event_mail.mail_registration_ids.mapped("mail_sent")))
