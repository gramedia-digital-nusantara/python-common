class ReadWriteRouter:
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica.
        """
        return 'replica'

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        This to allow mismatched using DB
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
