from pathlib import Path
from typing import TypedDict

from langchain_community.utilities.redis import get_client
from langchain_core.language_models.chat_models import BaseChatModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


from contextqa import logger
from contextqa.models.schemas import Status, ComponentsStatus
from contextqa.utils.clients import StoreClient
from contextqa.utils.settings import get_or_set


class _StatusDict(TypedDict):
    media_dir: Status
    db: Status
    vectordb: Status
    llm: Status
    redis: Status


class _StatusChecker:

    def __init__(self, session: Session, llm: BaseChatModel, vectordb_client: StoreClient):
        self.session = session
        self.statuses: _StatusDict = {}
        self.llm = llm
        self.vectordb_client = vectordb_client

    def check_media_dir(self):
        """Check if the media directory exists and have the correct permissions

        Returns
        -------
        Self
        """
        media_dir = get_or_set("extra").media_dir
        folder = Path(media_dir)
        try:
            test_file = folder / "dummy"
            # Attempt to open the file for reading and writing
            with test_file.open("w+") as f:
                f.write("Testing access")
            test_file.unlink()
            self.statuses["media_dir"] = Status.OK
        except Exception as ex:
            self.statuses["media_dir"] = Status.FAIL
            logger.warning("media dir check failed: %s", ex)
        return self

    def check_db(self):
        """Check if the database is up and running

        Returns
        -------
        self
        """
        try:
            self.session.execute(text("SELECT 1"))
            self.statuses["db"] = Status.OK
        except OperationalError as ex:
            self.statuses["db"] = Status.FAIL
            logger.warning("db check failed: %s", ex)
        return self

    def check_redis(self):
        """Check if the redis server is up and running. If ContextQA is using the local memory, the redis status
        will be set as "IRRELEVANT"

        Returns
        -------
        self
        """
        settings = get_or_set("extra")
        if settings.memory.kind == "Local":
            self.statuses["redis"] = Status.IRRELEVANT
        else:
            try:
                redis_client = get_client(settings.memory.url)
                redis_client.get("ping")
                self.statuses["redis"] = Status.OK
            except Exception as ex:
                logger.warning("redis check failed: %s", ex)
                self.statuses["redis"] = Status.FAIL
        return self

    def check_llm(self):
        """Check if ContextQA have access to the LLM

        Returns
        -------
        self
        """
        try:
            self.llm.invoke("ping")
            self.statuses["llm"] = Status.OK
        except Exception as ex:
            self.statuses["llm"] = Status.FAIL
            logger.warning("llm check failed: %s", ex)
        return self

    def check_vectordb(self):
        """Check if the vectordb is up and running

        Returns
        -------
        self
        """
        self.statuses["vectordb"] = Status.OK if self.vectordb_client.is_alive() else Status.FAIL
        return self

    def build(self) -> ComponentsStatus:
        """Build the final object

        Returns
        -------
        ComponentsStatus
        """
        return ComponentsStatus(**self.statuses)


def get_status(session: Session, model: BaseChatModel, vectordb_client: StoreClient) -> ComponentsStatus:
    """Return a summary of ContextQA's components status

    Parameters
    ----------
    session : Session
        Relational DB connection
    model : BaseChatModel
        Chat model
    vectordb_client : StoreClient
        Vector DB connection

    Returns
    -------
    ComponentsStatusS
    """
    checker = _StatusChecker(session, model, vectordb_client)
    return checker.check_media_dir().check_db().check_redis().check_llm().check_vectordb().build()
