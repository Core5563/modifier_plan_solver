"""module to run all that is connected with the destroying of problems"""
import os
from source.utility.problem_destroyer import ProblemDestroyer
from source.utility.directory_scanner import DirectoryScanner
from source.utility.db_handler import DBHandler

def destroy_problems_to_use():
    """destroy all problems"""
    scanner = DirectoryScanner()
    scanner.scan_for_directory("/var")
    #scanner.scan_for_directory("./")
    print(os.path.abspath("."))
    #file= os.open("/var/persist/eval.db", flags=os.O_RDWR)
    #file.close()
    pd = ProblemDestroyer("/var/persist/eval.db")
    pd.load_all_problems()
    pd.destroy_problems()
    pd.close()
    handler = DBHandler("/var/persist/eval.db")
    print(handler.get_all_destroyed_problems())
    print(handler.get_all_add_preconditions())


if __name__ == "__main__":
    destroy_problems_to_use()