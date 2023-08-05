from database import TextSecureDatabase
import dbmodel
import keyutils
import os
if __name__ == "__main__":
    db_path = "/home/tarek/config.db"
    newDb = not os.path.exists(db_path)

    tsb = TextSecureDatabase("sqlite:///%s" % db_path)
    tsb.init_db(dbmodel.Base)
    pku = keyutils.PreKeyUtil()
    if newDb:
        pku.generatePreKeys()