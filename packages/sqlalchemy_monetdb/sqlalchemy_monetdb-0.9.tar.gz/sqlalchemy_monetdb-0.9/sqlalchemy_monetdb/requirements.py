from sqlalchemy.testing.requirements import SuiteRequirements, exclusions


class Requirements(SuiteRequirements):
    @property
    def schemas(self):
        return exclusions.open()

    @property
    def sequences(self):
        return exclusions.open()

    @property
    def reflects_pk_names(self):
        return exclusions.open()

    @property
    def unicode_ddl(self):
        return exclusions.open()

    @property
    def datetime_microseconds(self):
        """monetdb doesn't support microsecond resolution"""
        return exclusions.closed()
    time_microseconds = datetime_microseconds

    @property
    def datetime_historic(self):
        return exclusions.open()

    @property
    def date_historic(self):
        return exclusions.open()

    @property
    def precision_numerics_enotation_small(self):
        return exclusions.open()

    @property
    def precision_numerics_enotation_large(self):
        """We don't support Numeric > 18"""
        return exclusions.closed()

    @property
    def view_reflection(self):
        return exclusions.open()

    @property
    def dbapi_lastrowid(self):
        return exclusions.open()

    @property
    def precision_numerics_retains_significant_digits(self):
        return exclusions.open()

    @property
    def sequences_optional(self):
        return exclusions.open()

