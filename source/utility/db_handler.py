import sqlite3
import os
class DBHandler:
    """handling of saving information"""
    def __init__(self):
        #remove file first
        try:
            os.remove('evaluation/database/eval.db')
        except FileNotFoundError:
            #ignore if file does not exist
            pass

        self.con = sqlite3.connect('evaluation/database/eval.db')
        self.curs: sqlite3.Cursor = self.con.cursor()
        scriptdata: str= ""
        with open("evaluation/database/setup.sql", mode="r", encoding="utf-8") as file:
            scriptdata = file.read().rstrip()
        self.curs.executescript(scriptdata)
    
    def get_all_destroyed_problems(self):
        """return all saved problem types"""
        res = self.curs.execute("SELECT * FROM destroyed_problems")
        return res.fetchall()
    
    def insert_destroy_problems(self, problem_filepath: str, domain_filepath: str, original_problem_filepath: str, original_domain_filepath: str)-> None:
        """insert into the destroyed problems table"""
        self.curs.execute(
            "INSERT INTO destroyed_problems(domainFilePath, problemFilePath, originalDomainFilePath, originalProblemFilePath) VALUES " +
            "(" +
            "\"" + domain_filepath + "\"," +
            "\"" + problem_filepath + "\"," +
            "\"" + original_domain_filepath + "\"," +
            "\"" + original_problem_filepath + "\"" +
            ")"
        )
    
    def find_corresponding_destroyed_problem_id(self, problem_filepath: str, domain_filepath: str, original_problem_filepath: str, original_domain_filepath: str)-> int:
        """returns problem id of the given problem"""
        res = self.curs.execute("SELECT destroyedProblemID FROM destroyed_problems WHERE " +
            "domainFilePath=\"" + domain_filepath +"\" " +
            "AND problemFilePath=\"" + problem_filepath + "\" " +
            "AND originalDomainFilePath=\"" + original_domain_filepath + "\" " +
            "AND originalProblemFilePath=\"" + original_problem_filepath + "\""
        )
        problem_id = res.fetchone()[0]
        return problem_id