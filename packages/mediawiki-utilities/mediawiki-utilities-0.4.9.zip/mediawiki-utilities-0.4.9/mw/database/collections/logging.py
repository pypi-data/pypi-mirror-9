import logging
import time
from itertools import chain

from ...types import Timestamp
from ...util import iteration, none_or
from .collection import Collection

logger = logging.getLogger("mw.database.collections.logging")
'''
class Logging(Collection):

    class Revisions(Collection):

        def query(self,
                  after=None, before=None, after_id=None, befor_id=None
                  page_id=None, user_id=None, user_text=None,
                  namespace=None, title=None, type=None, action=None,
                  direction=None, limit=None):
            """
            Queries revisions (excludes revisions to deleted pages)

            :Parameters:
                page_id : int
                    Page identifier.  Filter revisions to this page.
                user_id : int
                    User identifier.  Filter revisions to those made by this user.
                user_text : str
                    User text (user_name or IP address).  Filter revisions to those
                    made by this user.
                before : :class:`mw.Timestamp`
                    Filter revisions to those made before this timestamp.
                after : :class:`mw.Timestamp`
                    Filter revisions to those made after this timestamp.
                before_id : int
                    Filter revisions to those with an ID before this ID
                after_id : int
                    Filter revisions to those with an ID after this ID
                direction : str
                    "newer" or "older"
                limit : int
                    Limit the number of results

            :Returns:
                An iterator over revision rows.
            """
            start_time = time.time()

            page_id = none_or(page_id, int)
            user_id = none_or(user_id, int)
            user_text = none_or(user_text, str)
            before = none_or(before, Timestamp)
            after = none_or(after, Timestamp)
            before_id = none_or(before_id, int)
            after_id = none_or(after_id, int)
            direction = none_or(direction, levels=self.DIRECTIONS)
            include_page = bool(include_page)

            query = """
                SELECT *, FALSE AS archived FROM revision
            """

            if include_page:
                query += """
                    INNER JOIN page ON page_id = rev_page
                """

            query += """
                WHERE 1
            """
            values = []

            if page_id is not None:
                query += " AND rev_page = ? "
                values.append(page_id)
            if user_id is not None:
                query += " AND rev_user = ? "
                values.append(user_id)
            if user_text is not None:
                query += " AND rev_user_text = ? "
                values.append(user_text)
            if before is not None:
                query += " AND rev_timestamp < ? "
                values.append(before.short_format())
            if after is not None:
                query += " AND rev_timestamp > ? "
                values.append(after.short_format())
            if before_id is not None:
                query += " AND rev_id < ? "
                values.append(before_id)
            if after_id is not None:
                query += " AND rev_id > ? "
                values.append(after_id)

            if direction is not None:
                
                direction = ("ASC " if direction == "newer" else "DESC ")
                
                if before_id != None or after_id != None:
                    query += " ORDER BY rev_id {0}, rev_timestamp {0}".format(direction)
                else:
                    query += " ORDER BY rev_timestamp {0}, rev_id {0}".format(direction)

            if limit is not None:
                query += " LIMIT ? "
                values.append(limit)

            cursor = self.db.shared_connection.cursor()
            cursor.execute(query, values)
            count = 0
            for row in cursor:
                yield row
                count += 1

            logger.debug("%s revisions read in %s seconds" % (count, time.time() - start_time))
'''
