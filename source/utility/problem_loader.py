from source.utility.db_handler import DBHandler

class ProblemLoader:
    """for loading problems from ipc2016"""
    
    def __init__(self, db_file: str):
        self.db_handler = DBHandler(db_file)
    
    
