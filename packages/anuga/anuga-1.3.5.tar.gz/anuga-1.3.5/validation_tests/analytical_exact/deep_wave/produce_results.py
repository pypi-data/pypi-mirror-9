#--------------------------------
# import modules
#--------------------------------
import anuga
from anuga.validation_utilities import produce_report

args = anuga.get_args()

produce_report('run_wave.py', args=args)

