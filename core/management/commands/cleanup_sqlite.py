import os
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Safely deletes the local SQLite3 database file (db.sqlite3) once PostgreSQL is connected."

    def handle(self, *args, **options):
        db_engine = settings.DATABASES['default']['ENGINE']
        sqlite_file = Path(settings.BASE_DIR) / 'db.sqlite3'

        self.stdout.write(self.style.NOTICE(f"Current Database Engine: {db_engine}"))

        if 'postgresql' in db_engine or 'postgres' in db_engine:
            # Verify live PostgreSQL connection
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS("PostgreSQL connection verified successfully."))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Could not verify PostgreSQL connection: {e}\nAborting SQLite deletion for safety.")
                )
                return

            if sqlite_file.exists():
                try:
                    os.remove(sqlite_file)
                    self.stdout.write(
                        self.style.SUCCESS(f"Cleaned up legacy database: Deleted {sqlite_file}")
                    )
                except Exception as ex:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to delete {sqlite_file}: {ex}")
                    )
            else:
                self.stdout.write(self.style.SUCCESS("No legacy db.sqlite3 file found in project root."))
        else:
            self.stdout.write(
                self.style.WARNING("Active database is not PostgreSQL. SQLite file was preserved.")
            )
