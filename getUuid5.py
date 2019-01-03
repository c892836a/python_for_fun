import uuid
import getLogger


class GetUuid5:
    host_dns = uuid.NAMESPACE_DNS
    logger = None

    def __init__(self, host_dns):
        self.host_dns = uuid.uuid5(uuid.NAMESPACE_DNS, host_dns)
        self.logger = getLogger.GetLogger("Uuid5", "getUnid5").initial_logger()
        self.logger.info("use {} as host dns".format(host_dns))

    def get_Unid5_name(self, name):
        unid5_name = uuid.uuid5(self.host_dns, name)
        if str(unid5_name).strip() != "":
            self.logger.info("encode {} to {}".format(
                name, str(unid5_name.hex)))
            return str(unid5_name.hex)
        else:
            self.logger.error("Uuid5 transform error")
            return "Uuid5 transform error"
