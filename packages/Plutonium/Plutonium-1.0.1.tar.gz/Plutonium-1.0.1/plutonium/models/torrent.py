
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
import datetime

from plutonium.modules.orm.base import Base

class Torrent(Base):
    __tablename__ = 'torrents'

    id = Column(Integer, primary_key = True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable = False)
    name = Column(String(length=255))
    title = Column(String(length=255))
    link = Column(String(length=255))
    is_sent_out = Column(Boolean)
    added = Column(DateTime, default=datetime.datetime.now)

    feed = relationship("Feed", backref = backref('torrents', order_by=id))

    __content_path_variables = {}

    def update_path_vars(self, data):
        self.__content_path_variables.update(data)

    def fetch_download_dir(self):
        path = self.feed.target_path_pattern % self.__content_path_variables
        return path
