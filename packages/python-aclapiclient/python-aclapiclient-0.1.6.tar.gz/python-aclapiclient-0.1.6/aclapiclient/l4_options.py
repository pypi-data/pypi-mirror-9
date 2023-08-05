

class L4Opts(object):

    def __init__(self, operator, port, target):
        self.operator = operator
        self.port = port
        self.target = target

    def to_dict(self):
        start_end = "start" if self.operator in ["eq", "gt", "range"] else "end"
        data = {
            "{}-port-{}".format(self.target, start_end): self.port,
            "{}-port-op".format(self.target): self.operator,
            "log": 0
        }

        data = self._format_port_range(data)
        return data

    def _format_port_range(self, data):
        """
        Formats the data when a port range in given, the port range should look like: "100:200"
        This will make the start port as 100 and 200 as the end port.

        Returns the changed data.
        """
        if ":" in self.port:
            try:
                start, end = self.port.split(":")
            except Exception:
                raise ValueError("Wrong port range! Got {}".format(self.port))

            key = "{}-port-start".format(self.target)
            data[key] = start
            key = "{}-port-end".format(self.target)
            data[key] = end

        return data
