import anuga
from anuga.validation_utilities import produce_report

args = anuga.get_args()

produce_report('numerical_runup.py', args=args)

