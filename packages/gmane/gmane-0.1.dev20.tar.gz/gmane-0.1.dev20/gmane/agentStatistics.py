class AgentStatistics:
    def __init__(self,list_datastructures=None)
        if not list_datastructures:
            print("input datastructures, please")
        author_messages_=
        self.author_messages_= author_messages_= c.OrderedDict(sorted(list_datastructures.author_messages.items(), key=lambda x: len(x[1])))
        self.msg_sizes=author_messages_.values()
        self.authors_msg_sizes=author_messages_.keys()
        self.measureQuantiles()
    def measureQuantiles(self):
        pass
