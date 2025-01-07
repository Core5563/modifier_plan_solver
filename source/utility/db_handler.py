"""A module to help with the db utility"""
import sqlite3
import os
class DBHandler:
    """handling of saving information"""
    def __init__(self):
        #remove file first
        self.remove_db_file()
        self.con = sqlite3.connect('evaluation/database/eval.db')
        self.curs: sqlite3.Cursor = self.con.cursor()
        self.initialize_db()

    def initialize_db(self) -> None:
        """make first initialization of database"""
        scriptdata: str= ""
        with open("evaluation/database/setup.sql", mode="r", encoding="utf-8") as file:
            scriptdata = file.read().rstrip()
        self.curs.executescript(scriptdata)

    def remove_db_file(self) -> None:
        """remove db file"""
        try:
            os.remove('evaluation/database/eval.db')
        except FileNotFoundError:
            #ignore if file does not exist
            pass

    def get_all_destroyed_problems(self) -> list[tuple[int, str, str, str, str]]:
        """return all saved problem types"""
        res = self.curs.execute("SELECT * FROM destroyed_problems")
        return res.fetchall()

    def insert_destroy_problems(self, problem_filepath: str, domain_filepath: str,
            original_problem_filepath: str, original_domain_filepath: str)-> None:
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

    def find_corresponding_destroyed_problem_id(self, problem_filepath: str, domain_filepath: str,
            original_problem_filepath: str, original_domain_filepath: str)-> int:
        """returns problem id of the given problem"""
        res = self.curs.execute("SELECT destroyedProblemID FROM destroyed_problems WHERE " +
            "domainFilePath=\"" + domain_filepath +"\" " +
            "AND problemFilePath=\"" + problem_filepath + "\" " +
            "AND originalDomainFilePath=\"" + original_domain_filepath + "\" " +
            "AND originalProblemFilePath=\"" + original_problem_filepath + "\""
        )
        problem_id = res.fetchone()[0]
        return problem_id

    def insert_into_added_preconditions(self, destroyed_problem_id: int, action_name: str, fluent_name: str) -> None:
        """insert into added precondition table"""
        self.curs.execute("INSERT INTO added_preconditions(destroyedProblemID, actionName, fluentName) VALUES " +
            "(" + 
            str(destroyed_problem_id) + "," +
            "\"" + action_name + "\", " +
            "\"" + fluent_name + "\"" +
            ")"
        )

    def insert_into_results(self, destroyed_problem_id: int, modifier_version_id: int, time_in_milliseconds: int) -> None:
        """insert into results table"""
        self.curs.execute("INSERT INTO results(destroyedProblemID, modifierVersionID, timeInMilliseconds) VALUES " +
            "(" + 
            str(destroyed_problem_id) + "," +
            str(modifier_version_id) + "," +
            str(time_in_milliseconds) +
            ")"
        )

    def get_all_add_preconditions(self):
        """get all entries from the add_preconditions table"""
        res = self.curs.execute("SELECT * FROM added_preconditions")
        return res.fetchall()

    def get_all_from_results(self):
        """get all from results table"""
        res = self.curs.execute("SELECT * FROM results")
        return res.fetchall()
    
    def find_corresponding_result_id(self, destroyed_problem_id: int, modifier_version_id: int, time_in_milliseconds: int) -> int:
        """find resultID of the corresponding entries"""
        res = self.curs.execute("SELECT resultID FROM results WHERE " +
            "destroyedProblemID=" + str(destroyed_problem_id) + " " + 
            "AND modifierVersionID=" + str(modifier_version_id) + " " +
            "AND timeInMilliseconds=" + str(time_in_milliseconds)
        )
        result_id = res.fetchone()[0]
        return result_id

    def insert_into_left_preconditions_results(self, result_id: int, action_name: str, fluent_name: str) -> None:
        """insert data into left_precondition_results table"""
        self.curs.execute(
            "INSERT INTO left_preconditions_results(resultID, actionName, fluentName) VALUES " +
            "(" + 
            str(result_id) + ", " +
            "\"" + action_name + "\", " + 
            "\"" + fluent_name + "\"" + 
            ")"
        )

    def get_all_left_preconditions_results(self) -> list[int, str, str]:
        """get everything from the left_preconditions_results table"""
        res = self.curs.execute("SELECT * FROM left_preconditions_results")
        return res.fetchall()
