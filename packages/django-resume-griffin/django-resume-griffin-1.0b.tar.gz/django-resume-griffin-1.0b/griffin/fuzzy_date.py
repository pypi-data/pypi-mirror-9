from datetime import date

import logging
logger = logging.getLogger('to_terminal')

class FuzzyDate(date):

    def __new__(cls, month, year):
        month=int(month)
        year=int(year)
        logger.debug("Creating new fuzzy date with %d and %d"%(month, year))
        return super(FuzzyDate, cls).__new__(cls, year, month, 1)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return self.strftime('%Y-%m-%d')

    def as_sql(self):
        return self.strftime('%Y-%m-%d')

    @classmethod
    def from_sql(klass, sql):
        return sql

