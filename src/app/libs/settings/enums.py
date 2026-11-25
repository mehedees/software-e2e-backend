from enum import StrEnum


class DeploymentEnv(StrEnum):
    """Where a service is deployed. Read from `DEPLOYMENT_ENV`."""

    DEV = "dev"
    SIT = "sit"
    UAT = "uat"
    PROD = "prod"


class LogLevel(StrEnum):
    """Log level names, matching the stdlib `logging` names. Read from `LOG_LEVEL`."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
