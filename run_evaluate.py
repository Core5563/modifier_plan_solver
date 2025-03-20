"""evaluate everything"""
from source.utility.evaluation import eval_all

def eval():
    """run evaluation inside container"""
    db_file = "/var/persist/eval.db"
    eval_all(db_file)

if __name__ == "__main__":
    eval()
