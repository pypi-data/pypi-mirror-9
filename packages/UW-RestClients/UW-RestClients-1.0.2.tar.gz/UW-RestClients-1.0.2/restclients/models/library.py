from django.db import models


class MyLibAccount(models.Model):
    holds_ready = models.IntegerField(max_length=8)
    fines = models.DecimalField(max_digits=8, decimal_places=2)
    items_loaned = models.IntegerField(max_length=8)
    next_due = models.DateField(null=True)

    def get_next_due_date_str(self):
        """
        return next due date in the ISO format (yyyy-mm-dd).
        If the next_due is None, return None.
        """
        if self.next_due is not None:
            return str(self.next_due)
        return None

    def json_data(self,
                  use_abbr_week_month_day_format=False):
        return {'holds_ready': self.holds_ready,
                'fines': self.fines,
                'items_loaned': self.items_loaned,
                'next_due': self.get_next_due_date_str()
                }

    def __str__(self):
        return "{next_due: %s, holds_ready: %d, fines: %.2f, items_loaned: %d}" % (
            self.next_due, self.holds_ready, self.fines, self.items_loaned)
