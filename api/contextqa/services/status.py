from pathlib import Path

from langchain_community.utilities.redis import get_client
from langchain_core.language_models.chat_models import BaseChatModel
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


from contextqa import logger
from contextqa.models.schemas import Status, ComponentStatus
from contextqa.utils.clients import StoreClient
from contextqa.utils.settings import get_or_set


class _StatusChecker:

    def __init__(self, session: Session, llm: BaseChatModel, vectordb_client: StoreClient | None):
        self.session = session
        self.statuses: list[ComponentStatus] = []
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
        status: Status
        try:
            test_file = folder / "dummy"
            # Attempt to open the file for reading and writing
            with test_file.open("w+") as f:
                f.write("Testing access")
            test_file.unlink()
            status = Status.OK
        except Exception as ex:
            status = Status.FAIL
            logger.warning("media dir check failed: %s", ex)
        finally:
            self.statuses.append(ComponentStatus(name="Media directory", status=status))
        return self

    def check_db(self):
        """Check if the database is up and running

        Returnsmodel
        -------
        self
        """
        status: Status
        try:
            self.session.execute(text("SELECT 1"))
            status = Status.OK
        except OperationalError as ex:
            status = Status.FAIL
            logger.warning("db check failed: %s", ex)
        finally:
            self.statuses.append(ComponentStatus(name="Relational DB", status=status))
        return self

    def check_redis(self):
        """Check if the redis server is up and running. If ContextQA is using the local memory, the redis status
        will be set as "IRRELEVANT"

        Returns
        -------
        self
        """
        status: Status
        settings = get_or_set("extra")
        if settings.memory.kind == "Local":
            status = Status.IRRELEVANT
        else:
            try:
                redis_client = get_client(settings.memory.url)
                redis_client.get("ping")
                status = Status.OK
            except Exception as ex:
                logger.warning("redis check failed: %s", ex)
                status = Status.FAIL
        self.statuses.append(ComponentStatus(name="Redis", status=status))
        return self

    def check_llm(self):
        """Check if ContextQA have access to the LLM

        Returns
        -------
        self
        """
        status: Status
        try:
            self.llm.invoke("ping")
            status = Status.OK
        except Exception as ex:
            status = Status.FAIL
            logger.warning("llm check failed: %s", ex)
        finally:
            self.statuses.append(ComponentStatus(name="LLM", status=status))
        return self

    def check_vectordb(self):
        """Check if the vectordb is up and running

        Returns
        -------
        self
        """
        self.statuses.append(
            ComponentStatus(
                name="Vector DB",
                status=(
                    Status.OK if self.vectordb_client is not None and self.vectordb_client.is_alive() else Status.FAIL
                ),
            )
        )
        return self

    def build(self) -> list[ComponentStatus]:
        """Build the final object

        Returns
        -------
        list[ComponentStatus]
        """
        return self.statuses


def get_status(session: Session, model: BaseChatModel, vectordb_client: StoreClient | None) -> list[ComponentStatus]:
    """Return a summary of ContextQA's components status

    Parameters
    ----------
    session : Session
        Relational DB connection
    model : BaseChatModel
        Chat model
    vectordb_client : StoreClient | None
        Vector DB connection

    Returns
    -------
    list[ComponentStatus]
    """
    checker = _StatusChecker(session, model, vectordb_client)
    return checker.check_media_dir().check_db().check_redis().check_llm().check_vectordb().build()
