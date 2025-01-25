"""A module to help with the db utility"""
import sqlite3
import os
class DBHandler:
    """handling of saving information"""
    def __init__(self, database_file_filepath: str):
        #remove file first
        self.database_file_filepath: str = database_file_filepath
        self.con = sqlite3.connect(database_file_filepath)
        self.curs: sqlite3.Cursor = self.con.cursor()

    def commit(self):
        """commit pending transactions"""
        self.con.commit()

    def close(self):
        """close the connection"""
        self.con.commit()
        self.con.close()

    def initialize_db(self) -> None:
        """make first initialization of database"""
        scriptdata: str= ""
        with open("evaluation/database/setup.sql", mode="r", encoding="utf-8") as file:
            scriptdata = file.read().rstrip()
        self.curs.executescript(scriptdata)

    def remove_db_file(self) -> None:
        """remove db file"""
        try:
            os.remove(self.database_file_filepath)
        except FileNotFoundError:
            #ignore if file does not exist
            pass

    def get_all_destroyed_problems(self) -> list[tuple[int, str, str]]:
        """return all saved problem types"""
        res = self.curs.execute("SELECT * FROM destroyed_problems")
        return res.fetchall()

    def insert_into_original_problems(
                self,
                problem_filepath: str,
                domain_filepath: str,
                plan_solvable_cost: int,
                solve_time_milliseconds:int,
                error_text: str | None = None) -> None:
        """insert into original problem"""
        self.curs.execute(
            "INSERT INTO original_problems(domainFilePath, problemFilePath, planSolvableCost, timeInMilliseconds, errorText) VALUES " +
            "(" +
            "\"" + domain_filepath + "\"," +
            "\"" + problem_filepath + "\"," +
            str(plan_solvable_cost) + "," +
            str(solve_time_milliseconds) + "," +
            ( "NULL" if error_text is None else ("\"" + error_text.replace("\"", "#").replace("\n", "|") + "\"")) +
            ")"
        )
        self.commit()

    def get_original_problem_from_id(self, problem_id: int) -> tuple[str, str, int , int]:
        """
        get everything from original problem regarding a id
        returns (domain_path, problem_path, cost, time_in_milliseconds)
        """
        res = self.curs.execute(
            "SELECT domainFilePath," +
            "problemFilePath," +
            "planSolvableCost," +
            "timeInMilliseconds " +
            "FROM original_problems WHERE originalProblemID=" + str(problem_id))
        return_tuple = res.fetchone()
        return return_tuple

    def insert_destroy_problems(self, problem_id:int,  problem_filepath: str, domain_filepath: str, problem_content: str, domain_content: str, error_text: str | None = None)-> None:
        """insert into the destroyed problems table"""
        self.curs.execute(
            "INSERT INTO destroyed_problems(destroyedProblemID, domainFilePath, problemFilePath, domainContent, problemContent, errorText) VALUES " +
            "(" + str(problem_id) + "," +
            "\"" + domain_filepath + "\"," +
            "\"" + problem_filepath + "\"," +
            "\"" + domain_content + "\"," +
            "\"" + problem_content + "\"," +
            ( "NULL" if error_text is None else ("\"" + error_text.replace("\"", "#").replace("\n", "|") + "\"")) +
            ")"
        )
        self.commit()

    def find_corresponding_original_problem_id(self, problem_filepath: str, domain_filepath: str)-> int:
        """returns problem id of the given problem"""
        res = self.curs.execute("SELECT originalProblemID FROM original_problems WHERE " +
            "domainFilePath=\"" + domain_filepath +"\" " +
            "AND problemFilePath=\"" + problem_filepath + "\" "
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
        self.commit()

    def insert_into_results(self, destroyed_problem_id: int, modifier_version_id: int, time_in_milliseconds: int) -> None:
        """insert into results table"""
        self.curs.execute("INSERT INTO results(destroyedProblemID, modifierVersionID, timeInMilliseconds) VALUES " +
            "(" + 
            str(destroyed_problem_id) + "," +
            str(modifier_version_id) + "," +
            str(time_in_milliseconds) +
            ")"
        )
        self.commit()

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
        self.commit()

    def get_all_left_preconditions_results(self) -> list[tuple[int, str, str]]:
        """get everything from the left_preconditions_results table"""
        res = self.curs.execute("SELECT * FROM left_preconditions_results")
        return res.fetchall()

    def get_not_used_original_problem_ids(self) -> list[tuple[int]]:
        """get all ids from problems which have not been destroyed and worked in the load in phase"""
        res = self.curs.execute(
            "SELECT original_problems.originalProblemID FROM original_problems " + 
            "WHERE  original_problems.originalProblemID NOT IN (SELECT destroyedProblemID FROM destroyed_problems) " +
            "AND original_problems.errorText IS NULL" 
        )
        return res.fetchall()
