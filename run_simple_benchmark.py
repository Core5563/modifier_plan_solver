"""run the simple benchmark"""
from source.utility.db_handler import DBHandler
from source.utility.problem_destroyer import ProblemDestroyer
from source.utility.evaluation import eval_all

def run_simple_benchmark():
    """run the benchmark"""
    #db_file = "/var/persist/simpleEval.db"
    #db_file = "/var/persist/evalSomethingReduced.db"
    db_file = "/var/persist/secondTry.db"
    #db_handler = DBHandler(db_file)
    #db_handler.remove_db_file()
    #db_handler = DBHandler(db_file)
    #db_handler.initialize_db()
    #db_handler.close()
    problem_destroyer = ProblemDestroyer(db_file)
    problem_destroyer.load_all_problems_simple_benchmark()
    problem_destroyer.destroy_problems()
    problem_destroyer.close()
    eval_all(db_file)
    #db_handler = DBHandler(db_file)
    #db_handler.look_into()

if __name__ == '__main__':
    run_simple_benchmark()